import { Button } from "@/components/ui/button";
import { useChatMessages } from "@/hooks/use-chat-messages";
import { useResetTestScenario } from "@/hooks/test-scenario/use-test-scenarios";
import { useProfile } from "@/hooks/use-profile";
import { useUserTarget } from "@/context/UserTargetContext";
import { useState } from "react";
import { ConversationResetterDialog } from "./ConversationResetterDialog";
import { TestScenarioConversationResetterDialog } from "@/pages/test/components/TestScenarioConversationResetterDialog";

/**
 * ConversationResetter component
 * Allows the user to reset their conversation.
 *
 * Context-aware: reads from UserTargetContext to determine behavior.
 * - Regular mode: resets the logged-in user's chat messages via useChatMessages.
 * - Impersonating mode: resets the test scenario via useResetTestScenario.
 *
 * Used in: ChatControls (both regular and test scenario contexts).
 */
export const ConversationResetter = ({
  onResetSuccess,
}: {
  onResetSuccess?: () => void;
}) => {
  const { isImpersonating, scenarioId } = useUserTarget();
  const { profile } = useProfile();
  const userId = profile?.id;

  const { chatMessages, resetChatMessages, resetStatus } = useChatMessages();
  const messages = chatMessages || [];

  const { mutateAsync: resetScenario, isPending: isScenarioResetting } =
    useResetTestScenario();

  const [showDialog, setShowDialog] = useState(false);

  const handleOpenDialog = () => {
    setShowDialog(true);
  };

  const handleConfirmReset = async () => {
    if (isImpersonating && scenarioId) {
      try {
        await resetScenario(scenarioId);
        setShowDialog(false);
        if (onResetSuccess) onResetSuccess();
      } catch {
        // error handled by hook
      }
    } else {
      await resetChatMessages();
      setShowDialog(false);
    }
  };

  const handleCloseDialog = () => {
    setShowDialog(false);
  };

  if (!userId) return null;

  const isResetting = isImpersonating ? isScenarioResetting : resetStatus === "pending";
  const isDisabled = isImpersonating
    ? isScenarioResetting
    : messages.length === 0 || resetStatus === "pending";

  return (
    <>
      <Button
        variant="destructive"
        onClick={handleOpenDialog}
        disabled={isDisabled}
        className="bg-red-500/90"
      >
        {isImpersonating ? "Reset Test Conversation" : "Reset Conversation"}
      </Button>
      {isImpersonating ? (
        <TestScenarioConversationResetterDialog
          isOpen={showDialog}
          onClose={handleCloseDialog}
          onConfirm={handleConfirmReset}
          isResetting={isResetting}
        />
      ) : (
        <ConversationResetterDialog
          isOpen={showDialog}
          onClose={handleCloseDialog}
          onConfirm={handleConfirmReset}
          isResetting={isResetting}
        />
      )}
    </>
  );
};
