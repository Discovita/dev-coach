import React, { useState, useRef, useEffect, useCallback } from 'react';
import { CoachState, UserProfile, Message, CoachResponse } from '@/types/apiTypes';
import { CoachingState } from '@/types/enums';
import { apiClient } from '@/api/client';
import { ChatControls } from '@/pages/chat/components/ChatControls';
import { ChatMessages } from '@/pages/chat/components/ChatMessages';
import { initialMessage } from '@/constants/initialMessage';

interface Props {
  userId: string;
  initialMessages?: Message[];
  initialCoachState?: CoachState;
  onStateUpdate?: (newState: CoachState, response: CoachResponse) => void;
}

export const ChatInterface: React.FC<Props> = ({
  userId,
  initialMessages = [],
  initialCoachState,
  onStateUpdate,
}) => {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null) as React.RefObject<HTMLDivElement>;

  // Initialize coach state
  const [coachState, setCoachState] = useState<CoachState>(
    initialCoachState || {
      current_state: CoachingState.INTRODUCTION,
      user_profile: {
        name: userId,
        goals: [],
      } as UserProfile,
      identities: [],
      proposed_identity: null,
      current_identity_id: null,
      conversation_history: initialMessages,
      metadata: {},
    }
  );

  // Add initial message on mount if no messages exist
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([{ role: 'coach', content: initialMessage }]);
    }
  }, [messages.length]); // Include messages.length as dependency

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, []);

  // Scroll when messages change
  useEffect(scrollToBottom, [messages, scrollToBottom]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      const userMessage: Message = { role: 'user', content: content.trim() };
      setMessages(prev => [...prev, userMessage]);
      setIsLoading(true);

      try {
        // Send message without adding to conversation_history (backend will add it)
        const response = await apiClient.sendMessage(content, coachState);
        setMessages(prev => [...prev, { role: 'coach', content: response.message }]);
        setCoachState(response.coach_state);

        // Notify parent component about state update if callback provided
        if (onStateUpdate) {
          onStateUpdate(response.coach_state, response);
        }
      } catch (error) {
        console.error('Failed to send message:', error);
        setMessages(prev => [
          ...prev,
          { role: 'system', content: 'Error sending message. Please try again.' },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, coachState, onStateUpdate]
  );

  const handleIdentityChoice = useCallback(
    (response: string) => {
      sendMessage(response);
    },
    [sendMessage]
  );

  const handleSendMessage = useCallback(
    (content: string) => {
      sendMessage(content);
    },
    [sendMessage]
  );

  return (
    <div className="_ChatInterface flex flex-col h-[100vh] rounded-md overflow-hidden shadow-gold-md bg-gold-50 transition-shadow hover:shadow-gold-lg dark:rounded-none">
      <ChatMessages
        messages={messages}
        isLoading={isLoading}
        coachState={coachState}
        handleIdentityChoice={handleIdentityChoice}
        messagesEndRef={messagesEndRef}
      />
      <ChatControls
        isLoading={isLoading}
        onSendMessage={handleSendMessage}
        messages={messages}
        userId={userId}
        coachState={coachState}
      />
    </div>
  );
};
