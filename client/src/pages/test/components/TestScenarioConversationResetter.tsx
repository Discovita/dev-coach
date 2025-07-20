import { useState } from "react";
import { TestScenarioConversationResetterDialog } from "./TestScenarioConversationResetterDialog";
import { useResetTestScenario } from "@/hooks/test-scenario/use-test-scenarios";
import { useReactiveQueryData } from "@/hooks/useReactiveQueryData";
import { User } from "@/types/user";
import { Button } from "@/components/ui/button";


/**
 * TestScenarioConversationResetter component
 * Allows the user to reset (delete) their entire test scenario data.
 *
 * Step-by-step:
 * 1. Get the current user profile from the query cache (if needed for UI logic).
 * 2. Show a button to open the reset confirmation dialog if the user is logged in.
 * 3. When the dialog is open, user can confirm or cancel the reset.
 * 4. If confirmed, call the resetTestScenario mutation.
 * 5. Disable the button if the reset is in progress.
 * 6. Optionally, show feedback (e.g., loading state) while resetting.
 *
 * Used in: Any test or admin page where conversation reset is needed.
 */
export const TestScenarioConversationResetter = ({ scenarioId, onResetSuccess }: { scenarioId: string; onResetSuccess?: () => void }) => {
  // Get user profile from the query cache (optional, for UI logic)
  const profile = useReactiveQueryData<User>(["user", "profile"]);
  const userId = profile?.id;

  // Get the reset mutation and its status
  const { mutateAsync, isPending } = useResetTestScenario();

  // State for controlling the dialog
  const [showDialog, setShowDialog] = useState(false);

  // Handler for button click: open the dialog
  const handleOpenDialog = () => {
    setShowDialog(true);
  };

  // Handler for confirming reset in the dialog
  const handleConfirmReset = async () => {
    try {
      await mutateAsync(scenarioId);
      setShowDialog(false);
      if (onResetSuccess) onResetSuccess();
    } catch {
      // error is handled by the hook
    }
  };

  // Handler for closing the dialog (cancel or after reset)
  const handleCloseDialog = () => {
    setShowDialog(false);
  };

  // If no userId, show nothing (optional, can remove if not needed)
  if (!userId) return null;

  return (
    <>
      {/* Button to open the reset confirmation dialog */}
      <Button
        variant="destructive"
        onClick={handleOpenDialog}
        disabled={isPending}
        className="bg-red-500/90"
      >
        Reset Test Conversation
      </Button>
      {/* Confirmation dialog for resetting conversation */}
      <TestScenarioConversationResetterDialog
        isOpen={showDialog}
        onClose={handleCloseDialog}
        onConfirm={handleConfirmReset}
        isResetting={isPending}
      />
    </>
  );
};
