import React, { useRef, useEffect, useCallback } from "react";
import { TestScenarioChatControls } from "@/pages/test/components/TestScenarioChatControls";
import { ChatMessages } from "@/pages/chat/components/ChatMessages";
import { useTestScenarioChatMessages } from "@/hooks/test-scenario/use-test-scenario-chat-messages";
import { useQueryClient } from "@tanstack/react-query";
import { CoachRequest } from "@/types/coachRequest";

/**
 * TestScenarioChatInterface component
 * Handles the chat UI, message sending, and scrolling for a test scenario user.
 * - Uses test-scenario hooks for chat history, coach state, actions, and final prompt.
 * - Implements optimistic UI for message sending.
 * - Keeps 100% comment coverage for clarity.
 *
 * Props:
 *   userId: string - The id of the test scenario user.
 *   scenarioId: string - The id of the test scenario.
 *   onResetSuccess?: () => void - Optional callback after reset
 */
export const TestScenarioChatInterface: React.FC<{
  userId: string;
  scenarioId: string;
  onResetSuccess?: () => void;
}> = ({ userId, scenarioId, onResetSuccess }) => {
  // Reference to the end of the messages list for auto-scrolling
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  // Get chat messages for the test user (with optimistic UI support)
  const {
    chatMessages,
    componentConfig,
    isLoading,
    isError,
    updateChatMessages,
    updateStatus,
    pendingMessage,
    isPending,
  } = useTestScenarioChatMessages(userId);

  // Compose the messages to display, including the pending message if any (optimistic UI)
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
  }, [displayedMessages, scrollToBottom]);

  // Handler for sending a message
  const handleSendMessage = useCallback(
    async (request: CoachRequest) => {
      if (!request.message.trim() || updateStatus === "pending") return;
      
      // For test scenarios, always include the user_id to enable admin impersonation
      const requestWithUserId: CoachRequest = {
        ...request,
        user_id: userId,
      };
      
      await updateChatMessages(requestWithUserId);
    },
    [updateChatMessages, updateStatus, userId]
  );

  // Enhanced onResetSuccess: invalidate chat and coach state queries, then call parent callback
  const handleResetSuccess = useCallback(() => {
    queryClient.invalidateQueries({
      queryKey: ["testScenarioUser", userId, "chatMessages"],
    });
    queryClient.invalidateQueries({
      queryKey: ["testScenarioUser", userId, "coachState"],
    });
    if (onResetSuccess) onResetSuccess();
  }, [queryClient, userId, onResetSuccess]);

  // Loading and error states
  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        Loading test scenario chat...
      </div>
    );
  }
  if (isError) {
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
        messagesEndRef={messagesEndRef}
        componentConfig={componentConfig}
        onSendUserMessageToCoach={handleSendMessage}
        testUserId={userId}
      />
      <TestScenarioChatControls
        isProcessingMessage={isPending}
        onSendMessage={handleSendMessage}
        scenarioId={scenarioId}
        testUserId={userId}
        onResetSuccess={handleResetSuccess}
      />
    </div>
  );
};
