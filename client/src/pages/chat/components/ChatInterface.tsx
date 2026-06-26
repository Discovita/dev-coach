import { useUserTarget } from "@/context/UserTargetContext";
import { useChatMessages } from "@/hooks/use-chat-messages";
import { useCoachState } from "@/hooks/use-coach-state";
import { useProfile } from "@/hooks/use-profile";
import { isCoachingComplete } from "@/lib/studio-lock";
import {
	hasSeenStudioUnlock,
	markStudioUnlockSeen,
} from "@/lib/studio-unlock-seen";
import { ChatControls } from "@/pages/chat/components/ChatControls";
import { ChatMessages } from "@/pages/chat/components/ChatMessages";
import { ConversationExporter } from "@/pages/chat/components/ConversationExporter";
import { ConversationResetter } from "@/pages/chat/components/ConversationResetter";
import { StudioUnlockAnimation } from "@/pages/chat/components/StudioUnlockAnimation";
import { VisualizationChatGate } from "@/pages/chat/components/VisualizationChatGate";
import { TestScenarioSessionFreezer } from "@/pages/test/components/TestScenarioSessionFreezer";
import type { CoachRequest } from "@/types/coachRequest";
import type { Message } from "@/types/message";
import React, { useRef, useEffect, useCallback, useState } from "react";

interface ChatInterfaceProps {
	onResetSuccess?: () => void;
}

/**
 * ChatInterface component
 * Handles the chat UI, message sending, and scrolling.
 * - Uses useChatMessages for chat history and sending messages.
 * - Optimistically updates the UI when sending messages.
 * - Always fetches fresh chat history on mount.
 * - Keeps 100% comment coverage for clarity.
 */
export const ChatInterface: React.FC<ChatInterfaceProps> = ({
	onResetSuccess,
}) => {
	// Reference to the end of the messages list for auto-scrolling
	const messagesEndRef = useRef<HTMLDivElement>(null);

	// Admin-only freeze-session button: targets the impersonated test
	// user when inside a UserTargetProvider (TestChat), otherwise the
	// logged-in user (regular /chat). Hidden for non-admins.
	const { profile, isAdmin } = useProfile();
	const { isImpersonating, targetUserId } = useUserTarget();

	// Once coaching is complete (visualization phase reached AND the
	// visualization intro video acknowledged), the coach does nothing, so the
	// composer is replaced with a panel pointing the user to the Studio. Gating
	// on the intro-video ack — not the phase alone — keeps this from firing
	// before the I-Am outro video, the break, and the intro video have played.
	const { coachState } = useCoachState();
	const coachingComplete = isCoachingComplete(coachState);
	const freezeUserId = isImpersonating
		? targetUserId
		: profile?.id
			? String(profile.id)
			: null;

	// One-time Studio unlock takeover: plays the moment coaching completes
	// (visualization intro video acknowledged), then never again for this user.
	// The animation carries no Studio link — dismissing it reveals the
	// VisualizationChatGate below, which has the "Go to the Studio" button.
	// Keyed by the displayed user's id (freezeUserId) so it works under
	// impersonation too.
	const [showUnlock, setShowUnlock] = useState(false);
	useEffect(() => {
		if (coachingComplete && !hasSeenStudioUnlock(freezeUserId)) {
			setShowUnlock(true);
		}
	}, [coachingComplete, freezeUserId]);

	// Get chat messages and updateChatMessages mutation from the custom hook
	const {
		chatMessages,
		componentConfig,
		isLoading,
		isError,
		updateChatMessages,
		updateStatus,
	} = useChatMessages();

	// The optimistic user bubble is written into the query cache by
	// useChatMessages' `onMutate` (with a stable client id), so `chatMessages`
	// already includes it during a pending send — keeping a single source of
	// truth means the bubble's React key never changes between optimistic render
	// and commit, so it doesn't remount and flicker. We still sort defensively
	// in case history arrives out of order.
	const displayedMessages = React.useMemo<Message[]>(() => {
		return ((chatMessages ?? []) as Message[])
			.slice()
			.sort(
				(a, b) =>
					new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
			);
	}, [chatMessages]);

	// Keep the view pinned to the latest message. Use an INSTANT jump, not a
	// smooth scroll: a single message turn fires several rapid updates
	// (optimistic user message → loading bubble → the response, which can
	// collapse a card and add a new one), and an animated scroll chasing a list
	// whose height is changing under it is what made the chat feel jerky. A
	// single instant pin is stable. `displayedMessages` already derives from
	// `chatMessages`, so one effect covers both; `isProcessingMessage` re-pins
	// when the loading bubble appears/disappears.
	const scrollToBottom = useCallback(() => {
		messagesEndRef.current?.scrollIntoView({ block: "end" });
	}, []);

	useEffect(() => {
		scrollToBottom();
	}, [displayedMessages, updateStatus, scrollToBottom]);

	// Handler for sending a message.
	//
	// Coaching Phase Videos (PR 17): when `request.message` is `null`, the
	// dispatch is programmatic-only (video Continue button → ACK actions
	// without a user ChatMessage). Bypass the empty-string guard so the
	// request still reaches the orchestrator.
	const handleSendMessage = useCallback(
		async (request: CoachRequest) => {
			if (updateStatus === "pending") return;
			if (request.message !== null && !request.message.trim()) return;
			await updateChatMessages(request);
		},
		[updateChatMessages, updateStatus],
	);

	// If loading, show a loading state (optional)
	if (isLoading) {
		return (
			<div className="flex-1 flex items-center justify-center">
				Loading chat...
			</div>
		);
	}
	if (isError) {
		return (
			<div className="flex-1 flex items-center justify-center text-red-500">
				Error loading chat messages.
			</div>
		);
	}

	return (
		<div className="_ChatInterface flex flex-col h-full rounded-md overflow-hidden shadow-md bg-background transition-shadow hover:shadow-lg dark:rounded-none">
			{showUnlock && (
				<StudioUnlockAnimation
					onDismiss={() => {
						markStudioUnlockSeen(freezeUserId);
						setShowUnlock(false);
					}}
				/>
			)}
			<ChatMessages
				messages={displayedMessages}
				isProcessingMessage={updateStatus === "pending"}
				messagesEndRef={messagesEndRef}
				componentConfig={componentConfig}
				onSendUserMessageToCoach={handleSendMessage}
			/>
			{coachingComplete ? (
				<VisualizationChatGate />
			) : (
				<ChatControls
					isProcessingMessage={updateStatus === "pending"}
					onSendMessage={handleSendMessage}
				/>
			)}
			<div className="flex gap-2 p-2 border-t border-border bg-muted/50">
				<ConversationExporter />
				<ConversationResetter onResetSuccess={onResetSuccess} />
				{isAdmin && freezeUserId && (
					<TestScenarioSessionFreezer userId={freezeUserId} />
				)}
			</div>
		</div>
	);
};
