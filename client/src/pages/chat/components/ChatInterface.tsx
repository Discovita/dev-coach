import React, { useRef, useEffect, useCallback } from "react";
import { ChatControls } from "@/pages/chat/components/ChatControls";
import { ChatMessages } from "@/pages/chat/components/ChatMessages";
import { useChatMessages } from "@/hooks/use-chat-messages";
import { CoachRequest } from "@/types/coachRequest";

/**
 * ChatInterface component
 * Handles the chat UI, message sending, and scrolling.
 * - Uses useChatMessages for chat history and sending messages.
 * - Optimistically updates the UI when sending messages.
 * - Always fetches fresh chat history on mount.
 * - Keeps 100% comment coverage for clarity.
 */
export const ChatInterface: React.FC = () => {
  // Reference to the end of the messages list for auto-scrolling
  const messagesEndRef = useRef<HTMLDivElement>(null);

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

  // Handler for sending a message
  const handleSendMessage = useCallback(
    async (request: CoachRequest) => {
      if (!request.message.trim() || updateStatus === "pending") return;
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
    <div className="_ChatInterface flex flex-col h-[100vh] rounded-md overflow-hidden shadow-gold-md bg-gold-50 transition-shadow hover:shadow-gold-lg dark:rounded-none">
      <ChatMessages
        messages={displayedMessages}
        isProcessingMessage={updateStatus === "pending"}
        messagesEndRef={messagesEndRef}
        componentConfig={componentConfig}
        onSendUserMessageToCoach={handleSendMessage}
      />
      <ChatControls
        isProcessingMessage={updateStatus === "pending"}
        onSendMessage={handleSendMessage}
      />
    </div>
  );
};
