import { ADMIN_INVITES, COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";

/**
 * Admin Invites API
 * -----------------
 * Super-admin-only endpoints to manage email-bound invites.
 * Backend permission: IsSuperUser.
 *
 * Base: /api/v1/admin/invites
 */

export type InviteStatus = "pending" | "accepted" | "expired";

export interface Invite {
	id: string;
	email: string;
	status: InviteStatus;
	expires_at: string;
	accepted_at: string | null;
	invited_by_email: string | null;
	created_at: string;
}

export interface CreateInviteResult extends Invite {
	email_sent: boolean;
}

export async function fetchInvites(): Promise<Invite[]> {
	const response = await authFetch(`${COACH_BASE_URL}${ADMIN_INVITES}`);
	if (!response.ok) {
		throw new Error("Failed to fetch invites");
	}
	return response.json();
}

export async function createInvite(email: string): Promise<CreateInviteResult> {
	const response = await authFetch(`${COACH_BASE_URL}${ADMIN_INVITES}`, {
		method: "POST",
		body: JSON.stringify({ email }),
	});
	const data = await response.json();
	if (!response.ok) {
		throw new Error(data?.error ?? "Failed to create invite");
	}
	return data;
}

export async function resendInvite(id: string): Promise<CreateInviteResult> {
	const response = await authFetch(
		`${COACH_BASE_URL}${ADMIN_INVITES}/${id}/resend`,
		{ method: "POST" },
	);
	const data = await response.json();
	if (!response.ok) {
		throw new Error(data?.error ?? "Failed to resend invite");
	}
	return data;
}

export async function revokeInvite(id: string): Promise<void> {
	const response = await authFetch(`${COACH_BASE_URL}${ADMIN_INVITES}/${id}`, {
		method: "DELETE",
	});
	if (!response.ok) {
		throw new Error("Failed to revoke invite");
	}
}
