import type { AdminUserListItem } from "@/api/adminUsers";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useImpersonation } from "@/context/ImpersonationContext";
import { useAdminUsers } from "@/hooks/use-admin-users";
import { useProfile } from "@/hooks/use-profile";
import InvitesPanel from "@/pages/admin-users/components/InvitesPanel";
import { useNavigate } from "@tanstack/react-router";
import { Eye, FlaskConical, Loader2, Search } from "lucide-react";
import { useState } from "react";

/**
 * AdminUsers page
 *
 * Lists all users in the system with search/filter. Admins can click
 * "View As" to start impersonating a user, which switches all data hooks
 * to fetch that user's data via admin endpoints.
 *
 * Route: /admin/users
 */
export default function AdminUsers() {
	const { data: users, isLoading, isError } = useAdminUsers();
	const { startImpersonating, impersonatedUser } = useImpersonation();
	const { profile } = useProfile();
	const navigate = useNavigate();
	const [search, setSearch] = useState("");

	const filteredUsers = (users ?? []).filter((user) => {
		if (!search) return true;
		const term = search.toLowerCase();
		return (
			user.email.toLowerCase().includes(term) ||
			(user.first_name ?? "").toLowerCase().includes(term) ||
			(user.last_name ?? "").toLowerCase().includes(term) ||
			(user.coaching_phase ?? "").toLowerCase().includes(term) ||
			(user.test_scenario_name ?? "").toLowerCase().includes(term)
		);
	});

	const handleViewAs = (user: AdminUserListItem) => {
		startImpersonating({
			id: user.id,
			email: user.email,
			first_name: user.first_name,
			last_name: user.last_name,
		});
		navigate({ to: "/chat" });
	};

	const formatPhase = (phase: string | null) => {
		if (!phase) return null;
		return phase.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
	};

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
		<div className="max-w-5xl mx-auto">
			<div className="flex items-center justify-between mb-6">
				<div>
					<h1 className="text-2xl font-bold">Users</h1>
					<p className="text-sm text-muted-foreground mt-1">
						{users?.length ?? 0} total users
					</p>
				</div>
			</div>

			{/* Invites — super-admin only (backend also enforces IsSuperUser) */}
			{profile?.is_superuser && <InvitesPanel />}

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
								Phase
							</th>
							<th className="text-right font-medium px-4 py-3">Actions</th>
						</tr>
					</thead>
					<tbody className="divide-y divide-border">
						{filteredUsers.map((user) => {
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
												{formatPhase(user.coaching_phase)}
											</Badge>
										) : (
											<span className="text-muted-foreground text-xs">—</span>
										)}
									</td>
									<td className="px-4 py-3 text-right">
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
									</td>
								</tr>
							);
						})}
						{filteredUsers.length === 0 && (
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
		</div>
	);
}
