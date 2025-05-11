import { convertToXml, downloadXml } from "@/utils/xmlExport";
import { Button } from "@/components/ui/button";
import { useReactiveQueryData } from "@/hooks/useReactiveQueryData";
import { User } from "@/types/user";
import { Message } from "@/types/message";
import { CoachState } from "@/types/coachState";

export const ConversationExporter = () => {
  const profile = useReactiveQueryData<User>(["user", "profile"]);
  const userId = profile?.id;
  const messages =
    useReactiveQueryData<Message[]>(["user", "chatMessages"]) || [];
  const coachState = useReactiveQueryData<CoachState>(["user", "coachState"]);

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
