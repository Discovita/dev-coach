import { convertToXml, downloadXml } from "@/utils/xmlExport";
import { Button } from "@/components/ui/button";
import { useProfile } from "@/hooks/use-profile";
import { useChatMessages } from "@/hooks/use-chat-messages";
import { useCoachState } from "@/hooks/use-coach-state";

export const ConversationExporter = () => {
  const { profile } = useProfile();
  const userId = profile?.id;
  const { chatMessages } = useChatMessages();
  const messages = chatMessages || [];
  const { coachState } = useCoachState();

  // Handler for exporting conversation as XML
  const handleExport = () => {
    if (!userId || !coachState) return;
    const xmlContent = convertToXml(messages, userId, coachState);
    downloadXml(xmlContent);
  };

  // If no userId, show nothing
  if (!userId) return null;

  return (
    <Button onClick={handleExport} disabled={messages.length === 0}>
      Export Conversation
    </Button>
  );
};
