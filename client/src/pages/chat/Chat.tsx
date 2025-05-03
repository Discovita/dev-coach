import React from 'react';
import { ChatInterface } from '@/pages/chat/components/ChatInterface';
import { CoachState } from '@/types/apiTypes';

const Chat = () => {
  const userId = React.useMemo(() => Math.random().toString(36).substring(2, 15), []);
  const initialState: CoachState = {
    current_state: 'introduction',
    user_profile: {
      name: userId,
      goals: [],
    },
    identities: [],
    proposed_identity: null,
    current_identity_id: null,
    conversation_history: [],
    metadata: {},
  };

  return (
    <div className="relative z-10 flex flex-col h-full _TestChat">
      <div className="flex flex-col xl:flex-row items-start flex-1 min-h-0">
        <div className="flex flex-col w-full xl:flex-1 min-w-0 overflow-hidden h-full min-h-0 xl:mr-4">
          <ChatInterface userId={userId} initialCoachState={initialState} initialMessages={[]} />
        </div>
      </div>
    </div>
  );
};

export default Chat;
