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
import { TestScenario } from "@/types/testScenario";

interface DeleteTestScenarioDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  scenario: TestScenario | null;
  isDeleting: boolean;
}

export function DeleteTestScenarioDialog({
  isOpen,
  onClose,
  onConfirm,
  scenario,
  isDeleting,
}: DeleteTestScenarioDialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-[400px]">
        <DialogHeader>
          <DialogTitle className="text-red-700">Delete Test Scenario</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete this test scenario? This action is permanent and cannot be undone.
          </DialogDescription>
          <div className="font-semibold mb-1">
            {scenario?.name ? `${scenario.name}` : "(No name)"}
          </div>
          <div className="text-xs text-neutral-500 mb-2">
            {scenario?.description}
          </div>
        </DialogHeader>
        {isDeleting && (
          <div className="flex items-center gap-2 py-4">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm text-muted-foreground">
              Deleting scenario...
            </span>
          </div>
        )}
        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isDeleting}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={onConfirm}
            disabled={isDeleting}
          >
            {isDeleting ? "Deleting..." : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 