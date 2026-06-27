import { CoachMessage } from "@/pages/chat/components/CoachMessage";
import { LoadingBubbles } from "@/pages/chat/components/LoadingBubbles";
import { UserMessage } from "@/pages/chat/components/UserMessage";
import { CoachMessageWithComponent } from "@/pages/chat/components/coach-message-with-component/CoachMessageWithComponent.tsx";
import type { CoachRequest } from "@/types/coachRequest";
import type { ComponentConfig } from "@/types/componentConfig";
import type { Message } from "@/types/message";
import MarkdownRenderer from "@/utils/MarkdownRenderer";
import { AnimatePresence, motion } from "framer-motion";
import type React from "react";

/**
 * ChatMessages renders the conversation. See ChatInterface.tsx for the data
 * flow; loading state is represented as a `pending` coach message (the dots
 * bubble) rather than a separate element, so the dots and the eventual
 * response are ONE bubble whose content swaps in place.
 *
 * Props:
 * - messages: full chat history to render (includes the optimistic user
 *   message and the pending coach placeholder during a send)
 * - isProcessingMessage: whether a send is in flight (disables interactive cards)
 * - messagesEndRef: scroll anchor pinned to the bottom
 * - componentConfig: latest in-memory component for the newest coach message
 * - onSendUserMessageToCoach: handler for component button selection
 */
interface ChatMessagesProps {
	messages: Message[];
	isProcessingMessage: boolean;
	messagesEndRef: React.RefObject<HTMLDivElement | null>;
	componentConfig?: ComponentConfig | null;
	onSendUserMessageToCoach: (request: CoachRequest) => void;
}

// A soft ease-out that decelerates into place (easeOutExpo-ish).
const SMOOTH_EASE = [0.22, 1, 0.36, 1] as const;

// Slide-over entrance for a chosen canned option becoming the user's message.
// It starts to the LEFT of its final (right-aligned) spot and slides RIGHT into
// place at a constant (linear) pace, so it never passes the target and slides
// back. Deliberately slow (2s) for now so the motion is easy to see — tune down
// once the feel is dialed in. Only choice messages use this (see `fromChoice`).
const CHOICE_SLIDE_DISTANCE = 80;
const CHOICE_SLIDE_DURATION = 2;

// Each row fades in on mount and fades out on unmount — opacity only, NO
// `layout` animation. (We tried `layout`: animating a bubble's size by scaling
// it visibly distorts the text as it grows and, under popLayout, made the
// loading dots "fall" onto the composer. A plain opacity crossfade is calmer.)
// AnimatePresence uses the default in-flow mode so any rare exit fades in place.
// Stable keys mean existing rows never re-mount, so they never re-animate.
const rowMotion = {
	initial: { opacity: 0 },
	animate: { opacity: 1 },
	exit: { opacity: 0, transition: { duration: 0.2, ease: "easeIn" } },
	transition: { duration: 0.4, ease: SMOOTH_EASE },
} as const;

export const ChatMessages: React.FC<ChatMessagesProps> = ({
	messages,
	isProcessingMessage,
	messagesEndRef,
	componentConfig,
	onSendUserMessageToCoach,
}) => {
	// Picks the component (if any) to render for a non-pending coach message.
	const resolveCoachComponent = (
		message: Message,
		isLastCoachMessage: boolean,
	): ComponentConfig | null => {
		if (isLastCoachMessage) {
			// Prefer the in-memory cache when not processing (freshest server
			// response). Fall through to `message.component_config` for
			// server-seeded cards (welcome SESSION_VIDEO, post-END_BREAK intros) —
			// those represent persisted history and stay visible even during
			// in-flight requests, so clicking Continue doesn't blink the card out.
			return (
				(!isProcessingMessage && componentConfig) ||
				message.component_config ||
				null
			);
		}
		// All other coach messages: ONLY their own persisted component_config.
		return message.component_config || null;
	};

	return (
		<div className="_ChatMessages scrollbar not-last:flex-grow overflow-y-auto sm:p-6 bg-gold-50  dark:bg-[#333333]">
			<AnimatePresence initial={false}>
				{messages.map((message: Message, index: number) => {
					// Only a freshly-chosen canned option slides over to become the
					// user's message; everything else (typed messages, coach messages)
					// just fades in.
					const slidesOver =
						message.role === "user" && message.fromChoice === true;
					return (
						<motion.div
							key={message.id ?? `${message.timestamp}-${message.role}`}
							initial={{ opacity: 0, x: slidesOver ? -CHOICE_SLIDE_DISTANCE : 0 }}
							animate={{ opacity: 1, x: 0 }}
							exit={rowMotion.exit}
							transition={
								slidesOver
									? { duration: CHOICE_SLIDE_DURATION, ease: "linear" }
									: rowMotion.transition
							}
						>
							{message.role === "coach" ? (
								// One persistent bubble: the dots crossfade to the response
								// (mode="wait" → dots fully fade before content fades in).
								<AnimatePresence mode="wait" initial={false}>
									{message.pending ? (
										<motion.div
											key="dots"
											initial={{ opacity: 0 }}
											animate={{ opacity: 1 }}
											exit={{ opacity: 0 }}
											transition={{ duration: 0.2 }}
										>
											<CoachMessage>
												<LoadingBubbles />
											</CoachMessage>
										</motion.div>
									) : (
										<motion.div
											key="content"
											initial={{ opacity: 0 }}
											animate={{ opacity: 1 }}
											transition={{ duration: 0.3, ease: SMOOTH_EASE }}
										>
											{(() => {
												const isLastCoachMessage =
													index === messages.length - 1;
												const componentToRender = resolveCoachComponent(
													message,
													isLastCoachMessage,
												);
												return componentToRender ? (
													<CoachMessageWithComponent
														componentConfig={componentToRender}
														onSendUserMessageToCoach={onSendUserMessageToCoach}
														disabled={isProcessingMessage}
													>
														<MarkdownRenderer content={message.content} />
													</CoachMessageWithComponent>
												) : (
													<CoachMessage>
														<MarkdownRenderer content={message.content} />
													</CoachMessage>
												);
											})()}
										</motion.div>
									)}
								</AnimatePresence>
							) : message.role === "user" ? (
								<UserMessage>{message.content}</UserMessage>
							) : (
								<div className="mb-4 p-3.5 pr-4 pl-4 rounded-[18px] max-w-[85%] leading-[1.5] shadow-sm break-words mx-auto bg-red-500/70 text-center font-medium">
									{message.content}
								</div>
							)}
						</motion.div>
					);
				})}
			</AnimatePresence>
			{/* Dummy div to scroll to bottom */}
			<div ref={messagesEndRef} />
		</div>
	);
};
