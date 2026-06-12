import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { adminUpdateIdentity, updateIdentity } from "@/api/identities";
import { useUserTarget } from "@/context/UserTargetContext";
import type { Identity, UpdateIdentityRequest } from "@/types/identity";
import { IdentityCategory } from "@/enums/identityCategory";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
} from "@/components/ui/select";
import { CategoryPill } from "./CategoryPill";

/**
 * Inline edit form for a single identity's name, category, and I AM statement.
 *
 * Mirrors the scene-save pattern in Images.tsx: writes through the regular
 * endpoint, or the admin endpoint when impersonating a test user, then
 * invalidates the identities query so both /identities and /iams refresh.
 * Calls `onDone()` after a successful save or when cancelled.
 */
export function IdentityEditForm({
	identity,
	onDone,
}: {
	identity: Identity;
	onDone: () => void;
}) {
	const { isImpersonating, queryKeyPrefix } = useUserTarget();
	const queryClient = useQueryClient();

	const [name, setName] = useState(identity.name ?? "");
	const [category, setCategory] = useState<IdentityCategory>(
		identity.category as IdentityCategory,
	);
	const [iAmStatement, setIAmStatement] = useState(
		identity.i_am_statement ?? "",
	);
	const [isSaving, setIsSaving] = useState(false);

	const handleSave = async () => {
		if (!identity.id) return;
		if (!name.trim()) {
			toast.error("Name can't be empty");
			return;
		}

		setIsSaving(true);
		try {
			const payload: UpdateIdentityRequest = {
				name: name.trim(),
				category,
				i_am_statement: iAmStatement.trim() || null,
			};

			if (isImpersonating) {
				await adminUpdateIdentity(identity.id, payload);
			} else {
				await updateIdentity(identity.id, payload);
			}

			queryClient.invalidateQueries({
				queryKey: [...queryKeyPrefix, "identities"],
			});
			toast.success("Identity updated");
			onDone();
		} catch (error) {
			toast.error("Failed to update identity");
			console.error("Failed to update identity:", error);
		} finally {
			setIsSaving(false);
		}
	};

	return (
		<div className="space-y-6">
			{/* Name + Category sit side by side on wider screens, stacked on small */}
			<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
				<div className="space-y-2">
					<Label htmlFor="identity-name">Name</Label>
					<Input
						id="identity-name"
						value={name}
						onChange={(e) => setName(e.target.value)}
						placeholder="e.g. Creative Visionary"
					/>
				</div>

				<div className="space-y-2">
					<Label htmlFor="identity-category">Category</Label>
					<Select
						value={category}
						onValueChange={(v) => setCategory(v as IdentityCategory)}
					>
						<SelectTrigger id="identity-category" className="w-full">
							<CategoryPill category={category} />
						</SelectTrigger>
						<SelectContent>
							{Object.values(IdentityCategory).map((cat) => (
								<SelectItem key={cat} value={cat}>
									<CategoryPill category={cat} />
								</SelectItem>
							))}
						</SelectContent>
					</Select>
				</div>
			</div>

			<div className="space-y-2">
				<Label htmlFor="identity-i-am">I AM Statement</Label>
				<Textarea
					id="identity-i-am"
					value={iAmStatement}
					onChange={(e) => setIAmStatement(e.target.value)}
					rows={4}
					placeholder="I am ..."
				/>
			</div>

			<div className="flex items-center gap-3">
				<Button onClick={handleSave} disabled={isSaving}>
					{isSaving ? "Saving..." : "Save"}
				</Button>
				<Button variant="outline" onClick={onDone} disabled={isSaving}>
					Cancel
				</Button>
			</div>
		</div>
	);
}
