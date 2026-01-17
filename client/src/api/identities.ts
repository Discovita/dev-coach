import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";
import { Identity } from "@/types/identity";

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

/**
 * Update an identity (partial update) for the current user.
 * PATCH /api/v1/identities/{id}
 * @param identityId - UUID of the identity to update
 * @param data - Partial identity data to update
 * @returns Updated Identity
 */
export async function updateIdentity(
  identityId: string,
  data: Partial<Identity>
): Promise<Identity> {
  const response = await authFetch(`${COACH_BASE_URL}/identities/${identityId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Failed to update identity" }));
    throw new Error(error.error || "Failed to update identity");
  }
  return response.json();
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
  data: Partial<Identity>
): Promise<Identity> {
  const response = await authFetch(`${COACH_BASE_URL}/admin/identities/update-identity`, {
    method: "PATCH",
    body: JSON.stringify({ identity_id: identityId, ...data }),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Failed to update identity" }));
    throw new Error(error.error || "Failed to update identity");
  }
  return response.json();
}
