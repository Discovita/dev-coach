import type { AdminUserListItem } from "@/api/adminUsers";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useImpersonation } from "@/context/ImpersonationContext";
import {
	type CoachingPhase,
	getCoachingPhaseDisplayName,
} from "@/enums/coachingPhase";
import { useAdminUsers, useDeleteUser } from "@/hooks/use-admin-users";
import { useProfile } from "@/hooks/use-profile";
import { DeleteUserDialog } from "@/pages/admin-users/components/DeleteUserDialog";
import {
	type PhaseSort,
	filterUsers,
	nextPhaseSort,
	sortUsersByPhase,
} from "@/pages/admin-users/user-list-helpers";
import { useNavigate } from "@tanstack/react-router";
import {
	ArrowDown,
	ArrowUp,
	ArrowUpDown,
	Eye,
	FlaskConical,
	Loader2,
	Search,
	Trash2,
} from "lucide-react";
import { useState } from "react";

/**
 * UsersPanel
 *
 * Searchable list of every user in the system. Test users are hidden until
 * the "Show test users" toggle is switched on, and the Phase column sorts by
 * coaching progression. Admins can click "View As" to start impersonating a
 * user, which switches all data hooks to fetch that user's data via admin
 * endpoints.
 */
export default function UsersPanel() {
	const { data: users, isLoading, isError } = useAdminUsers();
	const { startImpersonating, stopImpersonating, impersonatedUser } =
		useImpersonation();
	const { profile } = useProfile();
	const navigate = useNavigate();
	const deleteUser = useDeleteUser();
	const [search, setSearch] = useState("");
	const [showTestUsers, setShowTestUsers] = useState(false);
	const [phaseSort, setPhaseSort] = useState<PhaseSort>(null);
	const [userToDelete, setUserToDelete] = useState<AdminUserListItem | null>(
		null,
	);

	// Deleting is destructive and irreversible, so it follows the same
	// super-admin gate as invites and the Studio access override.
	const canDelete = profile?.is_superuser ?? false;

	const allUsers = users ?? [];
	const visibleUsers = sortUsersByPhase(
		filterUsers(allUsers, { search, showTestUsers }),
		phaseSort,
	);
	const hiddenTestUserCount = showTestUsers
		? 0
		: allUsers.filter((user) => user.is_test_user).length;

	const handleViewAs = (user: AdminUserListItem) => {
		startImpersonating({
			id: user.id,
			email: user.email,
			first_name: user.first_name,
			last_name: user.last_name,
		});
		navigate({ to: "/chat" });
	};

	const handleConfirmDelete = async () => {
		if (!userToDelete) return;
		const deletedId = userToDelete.id;
		try {
			await deleteUser.mutateAsync(deletedId);
			// Never leave the admin impersonating an account that no longer exists.
			if (impersonatedUser?.id === deletedId) stopImpersonating();
			setUserToDelete(null);
		} catch {
			// The dialog surfaces the mutation error and stays open.
		}
	};

	const handleCloseDeleteDialog = () => {
		deleteUser.reset();
		setUserToDelete(null);
	};

	const PhaseSortIcon =
		phaseSort === "asc"
			? ArrowUp
			: phaseSort === "desc"
				? ArrowDown
				: ArrowUpDown;

	if (isLoading) {
		return (
			<div className="flex items-center justify-center h-64">
				<Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
			</div>
		);
	}

	if (isError) {
		return (
			<div className="flex items-center justify-center h-64 text-destructive">
				Failed to load users.
			</div>
		);
	}

	return (
		<div>
			<div className="flex flex-wrap items-center justify-between gap-3 mb-4">
				<p className="text-sm text-muted-foreground">
					{visibleUsers.length} {visibleUsers.length === 1 ? "user" : "users"}
					{hiddenTestUserCount > 0 &&
						` · ${hiddenTestUserCount} test ${
							hiddenTestUserCount === 1 ? "user" : "users"
						} hidden`}
				</p>

				<div className="flex items-center gap-2">
					<Switch
						id="show-test-users"
						checked={showTestUsers}
						onCheckedChange={setShowTestUsers}
					/>
					<Label
						htmlFor="show-test-users"
						className="text-sm text-muted-foreground font-normal"
					>
						Show test users
					</Label>
				</div>
			</div>

			{/* Search */}
			<div className="relative mb-4">
				<Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
				<Input
					placeholder="Search by name, email, or coaching phase..."
					value={search}
					onChange={(e) => setSearch(e.target.value)}
					className="pl-9"
				/>
			</div>

			{/* Users table */}
			<div className="rounded-lg border border-border overflow-hidden">
				<table className="w-full text-sm">
					<thead>
						<tr className="bg-muted/50 border-b border-border">
							<th className="text-left font-medium px-4 py-3">User</th>
							<th className="text-left font-medium px-4 py-3 hidden md:table-cell">
								Type
							</th>
							<th className="text-left font-medium px-4 py-3 hidden md:table-cell">
								<button
									type="button"
									onClick={() => setPhaseSort(nextPhaseSort(phaseSort))}
									className="flex items-center gap-1.5 hover:text-foreground transition-colors"
									aria-label={
										phaseSort === "asc"
											? "Sort phase descending"
											: phaseSort === "desc"
												? "Clear phase sorting"
												: "Sort phase ascending"
									}
								>
									Phase
									<PhaseSortIcon
										className={`w-3.5 h-3.5 ${
											phaseSort ? "text-foreground" : "text-muted-foreground"
										}`}
									/>
								</button>
							</th>
							<th className="text-right font-medium px-4 py-3">Actions</th>
						</tr>
					</thead>
					<tbody className="divide-y divide-border">
						{visibleUsers.map((user) => {
							const isCurrentUser = user.id === profile?.id;
							const isCurrentlyImpersonating = impersonatedUser?.id === user.id;
							const displayName =
								user.first_name || user.last_name
									? `${user.first_name} ${user.last_name}`.trim()
									: null;

							return (
								<tr
									key={user.id}
									className={`hover:bg-muted/30 transition-colors ${
										isCurrentlyImpersonating
											? "bg-amber-50 dark:bg-amber-950/30"
											: ""
									}`}
								>
									<td className="px-4 py-3">
										<div className="flex flex-col gap-0.5">
											<div className="flex items-center gap-2">
												{displayName && (
													<span className="font-medium">{displayName}</span>
												)}
												{isCurrentUser && (
													<Badge variant="outline" className="text-xs">
														You
													</Badge>
												)}
												{user.is_staff && (
													<Badge variant="secondary" className="text-xs">
														Admin
													</Badge>
												)}
											</div>
											<span className="text-muted-foreground text-xs">
												{user.email}
											</span>
										</div>
									</td>
									<td className="px-4 py-3 hidden md:table-cell">
										{user.is_test_user ? (
											<div className="flex items-center gap-1.5">
												<FlaskConical className="w-3.5 h-3.5 text-orange-500 flex-shrink-0" />
												<span className="text-xs text-orange-700 dark:text-orange-400 font-medium truncate max-w-[180px]">
													{user.test_scenario_name ?? "Test"}
												</span>
											</div>
										) : (
											<span className="text-xs text-muted-foreground">
												Real user
											</span>
										)}
									</td>
									<td className="px-4 py-3 hidden md:table-cell">
										{user.coaching_phase ? (
											<Badge variant="outline" className="text-xs font-normal">
												{getCoachingPhaseDisplayName(
													user.coaching_phase as CoachingPhase,
												)}
											</Badge>
										) : (
											<span className="text-muted-foreground text-xs">—</span>
										)}
									</td>
									<td className="px-4 py-3 text-right">
										<div className="flex items-center justify-end gap-1">
											{isCurrentUser ? (
												<span className="text-xs text-muted-foreground">—</span>
											) : isCurrentlyImpersonating ? (
												<Badge className="bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900 dark:text-amber-200 dark:border-amber-700">
													Viewing
												</Badge>
											) : (
												<Button
													variant="ghost"
													size="sm"
													onClick={() => handleViewAs(user)}
													className="gap-1.5"
												>
													<Eye className="w-3.5 h-3.5" />
													View As
												</Button>
											)}
											{canDelete && !isCurrentUser && (
												<Button
													variant="ghost"
													size="sm"
													onClick={() => setUserToDelete(user)}
													className="text-muted-foreground hover:text-destructive"
													aria-label={`Delete ${user.email}`}
												>
													<Trash2 className="w-3.5 h-3.5" />
												</Button>
											)}
										</div>
									</td>
								</tr>
							);
						})}
						{visibleUsers.length === 0 && (
							<tr>
								<td
									colSpan={4}
									className="px-4 py-8 text-center text-muted-foreground"
								>
									{search ? "No users match your search." : "No users found."}
								</td>
							</tr>
						)}
					</tbody>
				</table>
			</div>

			<DeleteUserDialog
				user={userToDelete}
				onClose={handleCloseDeleteDialog}
				onConfirm={handleConfirmDelete}
				isDeleting={deleteUser.isPending}
				error={deleteUser.error as Error | null}
			/>
		</div>
	);
}
