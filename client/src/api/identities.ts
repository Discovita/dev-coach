import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";

/**
 * Download I Am Statements PDF for the authenticated user.
 * Calls GET /identities/download-i-am-statements-pdf/
 * Returns a Blob for file download.
 *
 * Used in: useDownloadIAmPdf hook
 */
export async function downloadIAmStatementsPdf(): Promise<Blob> {
  const response = await authFetch(
    `${COACH_BASE_URL}/identities/download-i-am-statements-pdf`,
    {}
  );
  if (!response.ok) throw new Error("Failed to download PDF");
  return response.blob();
}
