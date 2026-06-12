import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";
import { createLogger, LogLevel } from "@/lib/logger";
import type { Identity, UpdateIdentityRequest } from "@/types/identity";

const log = createLogger("identitiesApi", LogLevel.DEBUG);

/**
 * Update an identity's scene details.
 * Calls PATCH /identities/{id}
 *
 * @param identityId - The ID of the identity to update
 * @param data - The scene details to update (clothing, mood, setting)
 * @returns The updated identity
 */
export async function updateIdentity(
	identityId: string,
	data: UpdateIdentityRequest,
) {
	log.debug(`Updating identity ${identityId}`, data);
	const response = await authFetch(
		`${COACH_BASE_URL}/identities/${identityId}`,
		{
			method: "PATCH",
			body: JSON.stringify(data),
		},
	);
	if (!response.ok) {
		const errorText = await response.text();
		log.error(`Failed to update identity: ${errorText}`);
		throw new Error("Failed to update identity");
	}
	const result = await response.json();
	log.debug("Successfully updated identity", result);
	return result;
}

/**
 * Reorder the authenticated user's identities.
 * Calls POST /identities/reorder
 *
 * @param orderedIds - Identity IDs in the desired display order (first = top)
 * @returns The user's identities in the new order
 */
export async function reorderIdentities(
	orderedIds: string[],
): Promise<Identity[]> {
	log.debug("Reordering identities", orderedIds);
	const response = await authFetch(`${COACH_BASE_URL}/identities/reorder`, {
		method: "POST",
		body: JSON.stringify({ ordered_ids: orderedIds }),
	});
	if (!response.ok) {
		const errorText = await response.text();
		log.error(`Failed to reorder identities: ${errorText}`);
		throw new Error("Failed to reorder identities");
	}
	return response.json();
}

/**
 * Reorder another user's identities (admin only).
 * Used when impersonating a test user, since the regular reorder endpoint is
 * scoped to the logged-in user.
 * Calls POST /admin/identities/reorder
 *
 * @param userId - The user whose identities to reorder
 * @param orderedIds - Identity IDs in the desired display order (first = top)
 * @returns The user's identities in the new order
 */
export async function adminReorderIdentities(
	userId: string,
	orderedIds: string[],
): Promise<Identity[]> {
	log.debug(`Admin reordering identities for user ${userId}`, orderedIds);
	const response = await authFetch(
		`${COACH_BASE_URL}/admin/identities/reorder`,
		{
			method: "POST",
			body: JSON.stringify({ user_id: userId, ordered_ids: orderedIds }),
		},
	);
	if (!response.ok) {
		const errorText = await response.text();
		log.error(`Failed to admin-reorder identities: ${errorText}`);
		throw new Error("Failed to reorder identities");
	}
	return response.json();
}

/**
 * Delete one of the authenticated user's identities.
 * Calls DELETE /identities/{id}
 *
 * @param identityId - The ID of the identity to delete
 */
export async function deleteIdentity(identityId: string): Promise<void> {
	log.debug(`Deleting identity ${identityId}`);
	const response = await authFetch(
		`${COACH_BASE_URL}/identities/${identityId}`,
		{ method: "DELETE" },
	);
	if (!response.ok) {
		const errorText = await response.text();
		log.error(`Failed to delete identity: ${errorText}`);
		throw new Error("Failed to delete identity");
	}
}

/**
 * Delete any identity (admin only).
 * Used when impersonating a test user, since the regular delete endpoint is
 * scoped to the logged-in user.
 * Calls DELETE /admin/identities/delete-identity?identity_id={id}
 *
 * @param identityId - The ID of the identity to delete
 */
export async function adminDeleteIdentity(identityId: string): Promise<void> {
	log.debug(`Admin deleting identity ${identityId}`);
	const response = await authFetch(
		`${COACH_BASE_URL}/admin/identities/delete-identity?identity_id=${identityId}`,
		{ method: "DELETE" },
	);
	if (!response.ok) {
		const errorText = await response.text();
		log.error(`Failed to admin-delete identity: ${errorText}`);
		throw new Error("Failed to delete identity");
	}
}

/**
 * Update any identity (admin only, partial update).
 * Used for updating test user identities from admin pages.
 * PATCH /api/v1/admin/identities/update-identity
 * @param identityId - UUID of the identity to update
 * @param data - Partial identity data to update
 * @returns Updated Identity
 */
export async function adminUpdateIdentity(
	identityId: string,
	data: UpdateIdentityRequest,
): Promise<Identity> {
	log.debug(`Admin updating identity ${identityId}`, data);
	const response = await authFetch(
		`${COACH_BASE_URL}/admin/identities/update-identity`,
		{
			method: "PATCH",
			body: JSON.stringify({ identity_id: identityId, ...data }),
		},
	);
	if (!response.ok) {
		const error = await response
			.json()
			.catch(() => ({ error: "Failed to update identity" }));
		throw new Error(error.error || "Failed to update identity");
	}
	const result = await response.json();
	log.debug("Successfully admin-updated identity", result);
	return result;
}

/**
 * Download I Am Statements PDF.
 *
 * If userId is provided, calls the admin endpoint to get PDF for a specific user.
 * Otherwise, calls the regular endpoint for the authenticated user.
 *
 * Endpoints:
 * - Regular: GET /identities/download-i-am-statements-pdf/
 * - Admin: GET /admin/identities/download-i-am-statements-pdf-for-user/?user_id=<id>
 *
 * Used in: useDownloadIAmPdf hook
 *
 * @param userId - Optional user ID for admin downloads (test scenarios)
 * @returns Blob for file download
 */
export async function downloadIAmStatementsPdf(userId?: string): Promise<Blob> {
	const url = userId
		? `${COACH_BASE_URL}/admin/identities/download-i-am-statements-pdf-for-user?user_id=${userId}`
		: `${COACH_BASE_URL}/identities/download-i-am-statements-pdf`;

	const response = await authFetch(url, {});
	if (!response.ok) throw new Error("Failed to download PDF");
	return response.blob();
}
