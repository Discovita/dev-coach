import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Loader2 } from "lucide-react";

/**
 * Props for the ConversationResetterDialog component
 * @param isOpen - Whether the dialog is open
 * @param onClose - Function to call when the dialog is closed
 * @param onConfirm - Function to call when reset is confirmed
 * @param isResetting - Whether the reset is currently in progress
 */
interface ConversationResetterDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  isResetting: boolean;
}

/**
 * Dialog component for confirming conversation reset (deletion)
 * Shows loader during reset
 *
 * Step-by-step:
 * 1. Show a modal dialog when isOpen is true.
 * 2. Display a warning about resetting conversation history.
 * 3. Show a loader if isResetting is true.
 * 4. Confirm and Cancel buttons: Confirm triggers onConfirm, Cancel triggers onClose.
 * 5. Confirm button is disabled while isResetting.
 */
export function ConversationResetterDialog({
  isOpen,
  onClose,
  onConfirm,
  isResetting,
}: ConversationResetterDialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      {/* Modal content with fixed width for readability */}
      <DialogContent className="max-w-[400px]">
        <DialogHeader>
          <DialogTitle className="text-red-700">Reset Conversation</DialogTitle>
          <DialogDescription>
            Are you sure you want to reset your conversation history?
            <br />
            <span className="font-semibold text-red-700">
              This action cannot be undone.
            </span>
          </DialogDescription>
        </DialogHeader>
        {isResetting && (
          <div className="flex items-center gap-2 py-4">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm text-muted-foreground">
              Resetting conversation...
            </span>
          </div>
        )}
        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isResetting}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={onConfirm}
            disabled={isResetting}
          >
            {isResetting ? "Resetting..." : "Reset"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 