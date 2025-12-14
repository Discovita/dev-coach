import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";

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
