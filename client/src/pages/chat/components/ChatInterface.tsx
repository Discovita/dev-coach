import React, { useRef, useEffect, useCallback } from "react";
import { ChatControls } from "@/pages/chat/components/ChatControls";
import { VisualizationChatGate } from "@/pages/chat/components/VisualizationChatGate";
import { ChatMessages } from "@/pages/chat/components/ChatMessages";
import { useChatMessages } from "@/hooks/use-chat-messages";
import { useCoachState } from "@/hooks/use-coach-state";
import { isCoachingComplete } from "@/lib/studio-lock";
import { ConversationExporter } from "@/pages/chat/components/ConversationExporter";
import { ConversationResetter } from "@/pages/chat/components/ConversationResetter";
import { TestScenarioSessionFreezer } from "@/pages/test/components/TestScenarioSessionFreezer";
import { useProfile } from "@/hooks/use-profile";
import { useUserTarget } from "@/context/UserTargetContext";
import type { CoachRequest } from "@/types/coachRequest";

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
export const ChatInterface: React.FC<ChatInterfaceProps> = ({ onResetSuccess }) => {
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

  // Get chat messages and updateChatMessages mutation from the custom hook
  const {
    chatMessages,
    componentConfig,
    isLoading,
    isError,
    updateChatMessages,
    updateStatus,
    pendingMessage, // The message being sent (if any)
    isPending, // Whether a message is being sent
  } = useChatMessages();

  // Compose the messages to display, including the pending message if any
  // Always sort by timestamp to ensure correct order, as backend/hook may not guarantee order
  const displayedMessages = React.useMemo(() => {
    let messages: { role: string; content: string; timestamp: string }[] =
      chatMessages || [];
    if (isPending && pendingMessage?.message) {
      messages = [
        ...messages,
        {
          role: "user",
          content: pendingMessage.message,
          timestamp: new Date().toISOString(), // Temporary timestamp
        },
      ];
    }
    // Sort by timestamp ascending (oldest first)
    return messages
      .slice()
      .sort(
        (a, b) =>
          new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      );
  }, [chatMessages, isPending, pendingMessage]);

  // Scroll to bottom when messages change
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages, scrollToBottom]);

  // Scroll to bottom when optimistic user message is added
  // This ensures the UI scrolls for both server and optimistic updates
  useEffect(() => {
    scrollToBottom();
  }, [displayedMessages, scrollToBottom]);

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
    [updateChatMessages, updateStatus]
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
