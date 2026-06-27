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

// A soft ease-out that decelerates into place (easeOutExpo-ish) — used for
// entrances and for the `layout` resize tweens so size changes glide.
const SMOOTH_EASE = [0.22, 1, 0.36, 1] as const;

// Each row fades in on mount, fades out on unmount, and — via the `layout`
// prop on the motion.div — smoothly tweens its own size/position changes
// rather than popping. Two places this matters: (1) an interactive card
// collapsing to its display-only form after the user answers, and (2) the
// pending coach bubble growing from the loading dots to the full response as
// its inner content swaps. Stable keys mean existing rows never re-mount, so
// `layout` only ever animates real size changes. AnimatePresence here uses the
// default (in-flow) mode — NOT popLayout — so a rare exit fades in place
// instead of being absolutely positioned and "falling" over the composer.
const rowMotion = {
	initial: { opacity: 0 },
	animate: { opacity: 1 },
	exit: { opacity: 0, transition: { duration: 0.2, ease: "easeIn" } },
	transition: {
		duration: 0.4,
		ease: SMOOTH_EASE,
		layout: { duration: 0.4, ease: SMOOTH_EASE },
	},
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
					const isPendingCoach =
						message.role === "coach" && message.pending === true;

					return (
						<motion.div
							layout
							key={message.id ?? `${message.timestamp}-${message.role}`}
							initial={rowMotion.initial}
							animate={rowMotion.animate}
							exit={rowMotion.exit}
							// Stagger the dots in slightly behind the user's message so the
							// pair doesn't appear in the same jarring instant.
							transition={
								isPendingCoach
									? { ...rowMotion.transition, delay: 0.15 }
									: rowMotion.transition
							}
						>
							{message.role === "coach" ? (
								// One persistent bubble: the dots crossfade to the response
								// (mode="wait" → dots fully fade before content fades in) while
								// the row's `layout` animates the height growth.
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
