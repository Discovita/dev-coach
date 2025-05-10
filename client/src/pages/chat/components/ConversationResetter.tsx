import { Button } from "@/components/ui/button";
import { useChatMessages } from "@/hooks/use-chat-messages";
import { useReactiveQueryData } from "@/hooks/useReactiveQueryData";
import { User } from "@/types/user";
import { Message } from "@/types/message";
import { useState } from "react";
import { ConversationResetterDialog } from "./ConversationResetterDialog";

/**
 * ConversationResetter component
 * Allows the user to reset (delete) their entire conversation history.
 *
 * Step-by-step:
 * 1. Get the current user profile and chat messages from the query cache.
 * 2. Show a button to open the reset confirmation dialog if the user is logged in.
 * 3. When the dialog is open, user can confirm or cancel the reset.
 * 4. If confirmed, call the resetChatMessages mutation from useChatMessages.
 * 5. Disable the button if there are no messages or if the reset is in progress.
 * 6. Optionally, show feedback (e.g., loading state) while resetting.
 *
 * Used in: Any test or admin page where conversation reset is needed.
 */
export const ConversationResetter = () => {
  // Get user profile and chat messages from the query cache
  const profile = useReactiveQueryData<User>(["user", "profile"]);
  const userId = profile?.id;
  const messages =
    useReactiveQueryData<Message[]>(["user", "chatMessages"]) || [];

  // Get the reset mutation and its status
  const { resetChatMessages, resetStatus } = useChatMessages();

  // State for controlling the dialog
  const [showDialog, setShowDialog] = useState(false);

  // Handler for button click: open the dialog
  const handleOpenDialog = () => {
    setShowDialog(true);
  };

  // Handler for confirming reset in the dialog
  const handleConfirmReset = async () => {
    await resetChatMessages();
    setShowDialog(false);
  };

  // Handler for closing the dialog (cancel or after reset)
  const handleCloseDialog = () => {
    setShowDialog(false);
  };

  // If no userId, show nothing
  if (!userId) return null;

  return (
    <>
      {/* Button to open the reset confirmation dialog */}
      <Button
        variant="destructive"
        onClick={handleOpenDialog}
        disabled={messages.length === 0 || resetStatus === "pending"}
        className="bg-red-500/90"
      >
        Reset Conversation
      </Button>
      {/* Confirmation dialog for resetting conversation */}
      <ConversationResetterDialog
        isOpen={showDialog}
        onClose={handleCloseDialog}
        onConfirm={handleConfirmReset}
        isResetting={resetStatus === "pending"}
      />
    </>
  );
};
