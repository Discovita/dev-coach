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

interface ConversationResetterDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  isResetting: boolean;
}

export function ConversationResetterDialog({
  isOpen,
  onClose,
  onConfirm,
  isResetting,
}: ConversationResetterDialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-[400px]">
        <DialogHeader>
          <DialogTitle className="text-red-700">Reset Conversation</DialogTitle>
          <DialogDescription>
            Are you sure you want to reset your conversation history?
            <br />
            This will reset your entire chat history, remove all created
            identites, and start your coach experience over,
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
