import React, { useRef, useEffect, useCallback } from "react";
import { ChatControls } from "@/pages/chat/components/ChatControls";
import { ChatMessages } from "@/pages/chat/components/ChatMessages";
import { useTestScenarioUserChatMessages } from "@/hooks/test-scenario/use-test-scenario-user-chat-messages";
import { useTestScenarioUserCoachState } from "@/hooks/test-scenario/use-test-scenario-user-coach-state";

/**
 * TestScenarioChatInterface component
 * Handles the chat UI, message sending, and scrolling for a test scenario user.
 * - Uses test-scenario hooks for chat history, coach state, actions, and final prompt.
 * - Implements optimistic UI for message sending.
 * - Keeps 100% comment coverage for clarity.
 *
 * Props:
 *   userId: string - The id of the test scenario user.
 */
export const TestScenarioChatInterface: React.FC<{ userId: string }> = ({ userId }) => {
  // Reference to the end of the messages list for auto-scrolling
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Get chat messages for the test user (with optimistic UI support)
  const {
    chatMessages,
    isLoading,
    isError,
    updateChatMessages,
    pendingMessage,
    isPending,
  } = useTestScenarioUserChatMessages(userId);

  // Get coach state for the test user
  const {
    coachState,
    isLoading: isLoadingCoachState,
    isError: isErrorCoachState,
    refetchCoachState,
  } = useTestScenarioUserCoachState(userId);

  // Compose the messages to display, including the pending message if any (optimistic UI)
  const displayedMessages = React.useMemo(() => {
    if (isPending && pendingMessage?.content) {
      return [
        ...(chatMessages || []),
        {
          role: "user",
          content: pendingMessage.content,
          timestamp: new Date().toISOString(),
        },
      ];
    }
    return chatMessages || [];
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
  }, [displayedMessages, scrollToBottom]);

  // Handler for sending a message using the mutation
  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isPending) return;
    await updateChatMessages({ content });
    // Optionally refetch coach state after sending
    await refetchCoachState();
  };

  // Handler for identity choice (if used)
  const handleIdentityChoice = (response: string) => {
    handleSendMessage(response);
  };

  // Loading and error states
  if (isLoading || isLoadingCoachState) {
    return (
      <div className="flex-1 flex items-center justify-center">
        Loading test scenario chat...
      </div>
    );
  }
  if (isError || isErrorCoachState) {
    return (
      <div className="flex-1 flex items-center justify-center text-red-500">
        Error loading test scenario chat data.
      </div>
    );
  }

  return (
    <div className="_TestScenarioChatInterface flex flex-col h-[100vh] rounded-md overflow-hidden shadow-gold-md bg-gold-50 transition-shadow hover:shadow-gold-lg dark:rounded-none">
      <ChatMessages
        messages={displayedMessages}
        isProcessingMessage={isPending}
        handleIdentityChoice={handleIdentityChoice}
        messagesEndRef={messagesEndRef}
        coachState={coachState}
      />
      <ChatControls
        isProcessingMessage={isPending}
        onSendMessage={handleSendMessage}
      />
    </div>
  );
}; 