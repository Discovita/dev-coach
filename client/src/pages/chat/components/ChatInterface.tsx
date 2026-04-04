import React, { useRef, useEffect, useCallback } from "react";
import { ChatControls } from "@/pages/chat/components/ChatControls";
import { ChatMessages } from "@/pages/chat/components/ChatMessages";
import { useChatMessages } from "@/hooks/use-chat-messages";
import { useUserTarget } from "@/context/UserTargetContext";
import { useQueryClient } from "@tanstack/react-query";
import { CoachRequest } from "@/types/coachRequest";

interface ChatInterfaceProps {
  onResetSuccess?: () => void;
}

/**
 * ChatInterface component
 * Handles the chat UI, message sending, and scrolling.
 *
 * Context-aware: reads from UserTargetContext to determine behavior.
 * - useChatMessages auto-switches endpoints and query keys via context.
 * - In impersonating mode, onResetSuccess triggers query invalidation
 *   and calls the parent callback.
 *
 * Used in: Chat page (regular) and TestChat (via UserTargetProvider).
 */
export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  onResetSuccess,
}) => {
  const { isImpersonating, targetUserId, queryKeyPrefix } = useUserTarget();
  const queryClient = useQueryClient();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    chatMessages,
    componentConfig,
    isLoading,
    isError,
    updateChatMessages,
    updateStatus,
    pendingMessage,
    isPending,
  } = useChatMessages();

  const displayedMessages = React.useMemo(() => {
    let messages: { role: string; content: string; timestamp: string }[] =
      chatMessages || [];
    if (isPending && pendingMessage?.message) {
      messages = [
        ...messages,
        {
          role: "user",
          content: pendingMessage.message,
          timestamp: new Date().toISOString(),
        },
      ];
    }
    return messages
      .slice()
      .sort(
        (a, b) =>
          new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      );
  }, [chatMessages, isPending, pendingMessage]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages, scrollToBottom]);

  useEffect(() => {
    scrollToBottom();
  }, [displayedMessages, scrollToBottom]);

  const handleSendMessage = useCallback(
    async (request: CoachRequest) => {
      if (!request.message.trim() || updateStatus === "pending") return;
      await updateChatMessages(request);
    },
    [updateChatMessages, updateStatus]
  );

  // When a test scenario is reset, invalidate the relevant caches then call parent callback
  const handleResetSuccess = useCallback(() => {
    if (isImpersonating) {
      queryClient.invalidateQueries({
        queryKey: [...queryKeyPrefix, "chatMessages"],
      });
      queryClient.invalidateQueries({
        queryKey: [...queryKeyPrefix, "coachState"],
      });
    }
    if (onResetSuccess) onResetSuccess();
  }, [queryClient, queryKeyPrefix, isImpersonating, onResetSuccess]);

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
    <div className="_ChatInterface flex flex-col h-[100vh] rounded-md overflow-hidden shadow-gold-md bg-gold-50 transition-shadow hover:shadow-gold-lg dark:rounded-none">
      <ChatMessages
        messages={displayedMessages}
        isProcessingMessage={updateStatus === "pending"}
        messagesEndRef={messagesEndRef}
        componentConfig={componentConfig}
        onSendUserMessageToCoach={handleSendMessage}
        testUserId={isImpersonating ? targetUserId! : undefined}
      />
      <ChatControls
        isProcessingMessage={updateStatus === "pending"}
        onSendMessage={handleSendMessage}
        onResetSuccess={handleResetSuccess}
      />
    </div>
  );
};
