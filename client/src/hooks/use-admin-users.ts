import {
	type AdminUserListItem,
	deleteUser,
	fetchAllUsers,
} from "@/api/adminUsers";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

/**
 * useAdminUsers hook
 *
 * Fetches and caches the full list of users for admin impersonation UI.
 * Only callable by admin users (backend enforces IsAdminUser).
 *
 * Used in: AdminUsers page
 */
export function useAdminUsers() {
	return useQuery<AdminUserListItem[]>({
		queryKey: ["admin", "users"],
		queryFn: fetchAllUsers,
		staleTime: 1000 * 60 * 5,
		retry: false,
	});
}

/**
 * useDeleteUser hook
 *
 * Permanently deletes a user, then refetches the admin user list so the
 * table reflects the deletion right away. Super-admin only (backend
 * enforces IsSuperUser).
 *
 * Used in: UsersPanel
 */
export function useDeleteUser() {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: deleteUser,
		onSuccess: () =>
			queryClient.invalidateQueries({ queryKey: ["admin", "users"] }),
	});
}
