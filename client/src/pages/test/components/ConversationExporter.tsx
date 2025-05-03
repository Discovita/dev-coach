import React from 'react';
import { Message, CoachState } from '@/types/apiTypes';
import { convertToXml, downloadXml } from '@/utils/xmlExport';
import { Button } from '@/components/ui/button';

interface Props {
  messages: Message[];
  userId: string;
  coachState: CoachState;
}

export const ConversationExporter: React.FC<Props> = ({ messages, userId, coachState }) => {
  const handleExport = () => {
    const xmlContent = convertToXml(messages, userId, coachState);
    downloadXml(xmlContent);
  };

  return (
    <Button onClick={handleExport} disabled={messages.length === 0}>
      Export Conversation
    </Button>
  );
};
