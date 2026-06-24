import { adminDeleteIdentity, deleteIdentity } from "@/api/identities";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog";
import { useUserTarget } from "@/context/UserTargetContext";
import type { Identity } from "@/types/identity";
import { useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { Trash2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

/**
 * Delete affordance for the identity detail page: a destructive trash button
 * that opens a confirmation dialog. On confirm it deletes via the regular
 * endpoint, or the admin endpoint when impersonating a test user, then
 * invalidates the identities query and navigates back to the list.
 */
export function IdentityDeleteButton({ identity }: { identity: Identity }) {
	const { isImpersonating, queryKeyPrefix } = useUserTarget();
	const queryClient = useQueryClient();
	const navigate = useNavigate();

	const [open, setOpen] = useState(false);
	const [isDeleting, setIsDeleting] = useState(false);

	const handleDelete = async () => {
		if (!identity.id) return;

		setIsDeleting(true);
		try {
			if (isImpersonating) {
				await adminDeleteIdentity(identity.id);
			} else {
				await deleteIdentity(identity.id);
			}

			queryClient.invalidateQueries({
				queryKey: [...queryKeyPrefix, "identities"],
			});
			toast.success("Identity deleted");
			setOpen(false);
			navigate({ to: "/identities" });
		} catch (error) {
			toast.error("Failed to delete identity");
			console.error("Failed to delete identity:", error);
		} finally {
			setIsDeleting(false);
		}
	};

	return (
		<Dialog open={open} onOpenChange={setOpen}>
			<DialogTrigger asChild>
				<Button
					variant="outline"
					size="sm"
					className="gap-2 text-destructive hover:text-destructive"
					aria-label="Delete identity"
					title="Delete identity"
				>
					<Trash2 className="h-4 w-4" />
					Delete
				</Button>
			</DialogTrigger>
			<DialogContent>
				<DialogHeader>
					<DialogTitle>Delete this identity?</DialogTitle>
					<DialogDescription>
						This permanently deletes
						{identity.name ? ` "${identity.name}"` : " this identity"} and its
						image. This can't be undone.
					</DialogDescription>
				</DialogHeader>
				<DialogFooter>
					<Button
						variant="outline"
						onClick={() => setOpen(false)}
						disabled={isDeleting}
					>
						Cancel
					</Button>
					<Button
						variant="destructive"
						onClick={handleDelete}
						disabled={isDeleting}
					>
						{isDeleting ? "Deleting..." : "Delete"}
					</Button>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	);
}
