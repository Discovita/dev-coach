import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import type { Prompt } from "@/types/prompt";
import { Loader2 } from "lucide-react";

interface DeletePromptDialogProps {
	isOpen: boolean;
	onClose: () => void;
	onConfirm: () => void;
	prompt: Prompt | null;
	isDeleting: boolean;
}

export function DeletePromptDialog({
	isOpen,
	onClose,
	onConfirm,
	prompt,
	isDeleting,
}: DeletePromptDialogProps) {
	return (
		<Dialog open={isOpen} onOpenChange={onClose}>
			<DialogContent className="max-w-[400px]">
				<DialogHeader>
					<DialogTitle className="text-red-700">Delete Prompt</DialogTitle>
					<DialogDescription>
						Are you sure you want to delete this prompt?
					</DialogDescription>
					<div className="font-semibold text-foreground mb-1">
						{prompt?.name ? `"${prompt.name}"` : "(No name)"}
					</div>
					<div className="text-xs text-muted-foreground mb-2">
						Coach State:{" "}
						<span className="font-semibold">{prompt?.coaching_phase}</span>
						{prompt?.version !== undefined && (
							<>
								{" | "}Version:{" "}
								<span className="font-semibold">{prompt.version}</span>
							</>
						)}
					</div>
				</DialogHeader>
				{isDeleting && (
					<div className="flex items-center gap-2 py-4">
						<Loader2 className="h-4 w-4 animate-spin" />
						<span className="text-sm text-muted-foreground">
							Deleting prompt...
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
