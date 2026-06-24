import { type AdminUserListItem, fetchAllUsers } from "@/api/adminUsers";
import { useQuery } from "@tanstack/react-query";

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
