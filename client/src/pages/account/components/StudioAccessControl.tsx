import { setStudioAccessOverride } from "@/api/testScenarioUser";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

/**
 * StudioAccessControl
 *
 * Super-admin-only control for overriding a user's Studio access. Rendered on
 * the Account page (for the viewed user — the impersonated user when an admin
 * is impersonating, otherwise the admin themselves).
 *
 * Tri-state override, mirroring `CoachState.studio_access_override`:
 *   - Default  (null)  → Studio unlocks automatically at the visualization phase
 *   - Unlocked (true)  → Studio always accessible
 *   - Locked   (false) → Studio always blocked
 *
 * Visibility is gated by the caller on the *logged-in* admin's `is_superuser`,
 * so the control stays available while impersonating.
 */

type Override = boolean | null;

const OPTIONS: { label: string; value: Override; hint: string }[] = [
	{
		label: "Default",
		value: null,
		hint: "Unlocks at the visualization phase",
	},
	{ label: "Unlocked", value: true, hint: "Always accessible" },
	{ label: "Locked", value: false, hint: "Always blocked" },
];

interface StudioAccessControlProps {
	/** The viewed user whose Studio access is being controlled. */
	userId: string;
	/** Current override value from the viewed user's coach state. */
	override: boolean | null | undefined;
}

export function StudioAccessControl({
	userId,
	override,
}: StudioAccessControlProps) {
	const queryClient = useQueryClient();
	const current: Override = override ?? null;

	const mutation = useMutation({
		mutationFn: (value: Override) => setStudioAccessOverride(userId, value),
		onSuccess: () => {
			// Refresh both the self and impersonated coach-state caches so the
			// sidebar Studio lock reflects the change immediately.
			queryClient.invalidateQueries({ queryKey: ["user", "coachState"] });
			queryClient.invalidateQueries({
				queryKey: ["testScenarioUser", userId, "coachState"],
			});
			toast.success("Studio access updated");
		},
		onError: (error) =>
			toast.error(
				error instanceof Error
					? error.message
					: "Failed to update Studio access",
			),
	});

	return (
		<div className="bg-card rounded-lg border p-6">
			<div className="flex items-center gap-2 mb-1">
				<h2 className="text-xl font-medium">Studio Access</h2>
				<span className="text-xs font-semibold uppercase tracking-wider text-[color:var(--nv-royal-purple)]/70 rounded-full border px-2 py-0.5">
					Super admin
				</span>
			</div>
			<p className="text-sm text-muted-foreground mb-4">
				Override Studio access for this user. By default the Studio unlocks
				automatically once they reach the identity visualization phase.
			</p>
			<div className="flex flex-col sm:flex-row gap-2">
				{OPTIONS.map((opt) => {
					const selected = current === opt.value;
					return (
						<button
							key={String(opt.value)}
							type="button"
							disabled={mutation.isPending || selected}
							onClick={() => mutation.mutate(opt.value)}
							className={`flex-1 rounded-lg border px-4 py-3 text-left transition-colors ${
								selected
									? "border-[var(--nv-royal-purple)] bg-[var(--nv-pale-lavender)]"
									: "border-border hover:bg-muted"
							} ${mutation.isPending ? "opacity-60" : ""}`}
						>
							<span className="block text-sm font-medium">{opt.label}</span>
							<span className="block text-xs text-muted-foreground mt-0.5">
								{opt.hint}
							</span>
						</button>
					);
				})}
			</div>
		</div>
	);
}
