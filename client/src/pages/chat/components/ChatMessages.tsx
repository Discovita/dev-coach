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
 * ChatMessages component is used to render the chat messages in both the
 *
 */

/**
 * Props for ChatMessages
 * ---------------------
 * - messages: The full chat message history to render (array of Message objects)
 * - isProcessingMessage: Whether a message is being sent (shows loading bubbles)
 * - coachState: The current coach state (for proposed identity)
 * - handleIdentityChoice: Handler for when a user selects an identity
 * - messagesEndRef: Ref to scroll to the bottom of the messages
 *
 * Used by: ChatInterface.tsx
 */
interface ChatMessagesProps {
	messages: Message[];
	isProcessingMessage: boolean;
	messagesEndRef: React.RefObject<HTMLDivElement | null>;
	/** Latest component config to render for the newest coach message (or null) */
	componentConfig?: ComponentConfig | null;
	/** Handler for component button selection (sends a CoachRequest) */
	onSendUserMessageToCoach: (request: CoachRequest) => void;
}

// A soft ease-out that decelerates into place (easeOutExpo-ish) — used for
// entrances and for the `layout` resize tweens below so size changes glide
// instead of snapping.
const SMOOTH_EASE = [0.22, 1, 0.36, 1] as const;

// Each row fades in on mount, fades out on unmount, and — via the `layout`
// prop on the motion.div — smoothly tweens its own size/position changes
// rather than popping. The classic example: when an interactive card (with
// buttons, full width) becomes its display-only version (no buttons, narrower)
// after the user answers, `layout` animates that resize. The list is wrapped
// in <AnimatePresence mode="popLayout"> so the one row that routinely unmounts
// — the loading bubble — gets pulled out of the layout flow as it fades, and
// the incoming coach response fades in over the same spot (a calm crossfade,
// not a hard dots→response cut). Stable keys (see `key` below) mean existing
// rows never re-mount, so `layout` only ever animates real size changes.
const rowMotion = {
	initial: { opacity: 0 },
	animate: { opacity: 1 },
	exit: { opacity: 0, transition: { duration: 0.2, ease: "easeIn" } },
	transition: {
		duration: 0.4,
		ease: SMOOTH_EASE,
		// Give the layout (resize) tween its own slightly springy timing so it
		// reads as a deliberate glide.
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
	return (
		<div className="_ChatMessages scrollbar not-last:flex-grow overflow-y-auto sm:p-6 bg-gold-50  dark:bg-[#333333]">
			<AnimatePresence mode="popLayout" initial={false}>
				{messages.map((message: Message, index: number) => (
					<motion.div
						layout
						key={message.id ?? `${message.timestamp}-${message.role}`}
						{...rowMotion}
					>
						{message.role === "coach" ? (
							(() => {
								const isLastCoachMessage = index === messages.length - 1;
								let componentToRender = null;

								if (isLastCoachMessage) {
									// Prefer the in-memory cache when not processing (freshest
									// server response). Fall through to `message.component_config`
									// for server-seeded cards (welcome SESSION_VIDEO,
									// post-END_BREAK intros) — those represent persisted
									// history and stay visible even during in-flight requests,
									// so clicking Continue doesn't blink the card out while
									// we wait for the response.
									componentToRender =
										(!isProcessingMessage && componentConfig) ||
										message.component_config ||
										null;
								} else {
									// For all other coach messages, ONLY check message.component_config
									componentToRender = message.component_config || null;
								}

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
							})()
						) : message.role === "user" ? (
							<UserMessage>{message.content}</UserMessage>
						) : (
							<div className="mb-4 p-3.5 pr-4 pl-4 rounded-[18px] max-w-[85%] leading-[1.5] shadow-sm break-words mx-auto bg-red-500/70 text-center font-medium">
								{message.content}
							</div>
						)}
					</motion.div>
				))}
				{isProcessingMessage && (
					<motion.div layout key="loading-bubbles" {...rowMotion}>
						<CoachMessage>
							<LoadingBubbles />
						</CoachMessage>
					</motion.div>
				)}
			</AnimatePresence>
			{/* Dummy div to scroll to bottom */}
			<div ref={messagesEndRef} />
		</div>
	);
};
