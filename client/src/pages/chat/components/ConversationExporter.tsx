import { Button } from "@/components/ui/button";
import { useChatMessages } from "@/hooks/use-chat-messages";
import { useCoachState } from "@/hooks/use-coach-state";
import { useProfile } from "@/hooks/use-profile";
import { convertToXml, downloadXml } from "@/utils/xmlExport";

export const ConversationExporter = () => {
	const { profile } = useProfile();
	const userId = profile?.id;
	const { chatMessages } = useChatMessages();
	const messages = chatMessages || [];
	const { coachState } = useCoachState();

	const handleExport = () => {
		if (!userId || !coachState) return;
		const xmlContent = convertToXml(messages, userId, coachState);
		downloadXml(xmlContent);
	};

	if (!userId) return null;

	return (
		<Button onClick={handleExport} disabled={messages.length === 0}>
			Export Conversation
		</Button>
	);
};
