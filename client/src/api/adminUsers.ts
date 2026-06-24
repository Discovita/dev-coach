import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";

/**
 * Admin Users API
 * ---------------
 * Admin-only endpoint to list all users with basic info.
 * Used by the admin Users page for impersonation.
 *
 * Endpoint: GET /api/v1/admin/test-user/all
 * Permission: IsAdminUser
 */

export interface AdminUserListItem {
	id: string;
	email: string;
	first_name: string;
	last_name: string;
	is_active: boolean;
	is_staff: boolean;
	is_superuser: boolean;
	last_login: string | null;
	created_at: string | null;
	coaching_phase: string | null;
	is_test_user: boolean;
	test_scenario_name: string | null;
}

export async function fetchAllUsers(): Promise<AdminUserListItem[]> {
	const response = await authFetch(`${COACH_BASE_URL}/admin/test-user/all`);
	if (!response.ok) {
		throw new Error("Failed to fetch users list");
	}
	return response.json();
}
