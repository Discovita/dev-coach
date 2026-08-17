import type { AdminUserListItem } from "@/api/adminUsers";
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

interface DeleteUserDialogProps {
	user: AdminUserListItem | null;
	onClose: () => void;
	onConfirm: () => void;
	isDeleting: boolean;
	error: Error | null;
}

/**
 * DeleteUserDialog
 *
 * Confirmation gate for permanently deleting a user from the admin Users
 * table. Open state is driven by `user` being non-null.
 */
export function DeleteUserDialog({
	user,
	onClose,
	onConfirm,
	isDeleting,
	error,
}: DeleteUserDialogProps) {
	const displayName =
		user && (user.first_name || user.last_name)
			? `${user.first_name} ${user.last_name}`.trim()
			: null;

	return (
		<Dialog
			open={user !== null}
			onOpenChange={(open) => {
				if (!open && !isDeleting) onClose();
			}}
		>
			<DialogContent className="max-w-[440px]">
				<DialogHeader>
					<DialogTitle className="text-destructive">Delete user</DialogTitle>
					<DialogDescription>
						This permanently deletes this user and everything attached to them —
						chat history, identities, coach state, notes, and generated images.
						This cannot be undone.
					</DialogDescription>
				</DialogHeader>

				<div className="rounded-md border border-border px-3 py-2">
					{displayName && <div className="font-medium">{displayName}</div>}
					<div className="text-xs text-muted-foreground">{user?.email}</div>
				</div>

				{error && <p className="text-sm text-destructive">{error.message}</p>}

				<DialogFooter>
					<Button variant="outline" onClick={onClose} disabled={isDeleting}>
						Cancel
					</Button>
					<Button
						variant="destructive"
						onClick={onConfirm}
						disabled={isDeleting}
						className="gap-1.5"
					>
						{isDeleting && <Loader2 className="w-4 h-4 animate-spin" />}
						{isDeleting ? "Deleting..." : "Delete permanently"}
					</Button>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	);
}
