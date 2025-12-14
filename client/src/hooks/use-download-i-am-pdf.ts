import { useMutation } from "@tanstack/react-query";
import { downloadIAmStatementsPdf } from "@/api/identities";

/**
 * useDownloadIAmPdf hook
 *
 * Handles downloading the I Am Statements PDF.
 * Uses TanStack Query's useMutation for managing loading state and errors.
 *
 * Step-by-step:
 * 1. Calls the downloadIAmStatementsPdf API function (with optional userId for admin)
 * 2. Creates a Blob URL from the response
 * 3. Triggers browser download via hidden anchor element
 * 4. Cleans up the Blob URL after download
 *
 * Usage:
 *   // For authenticated user's own PDF:
 *   const { downloadPdf, isDownloading, error } = useDownloadIAmPdf();
 *   <button onClick={() => downloadPdf()} disabled={isDownloading}>
 *     {isDownloading ? "Downloading..." : "Download PDF"}
 *   </button>
 *
 *   // For admin downloading a specific user's PDF (test scenarios):
 *   const { downloadPdf, isDownloading, error } = useDownloadIAmPdf();
 *   <button onClick={() => downloadPdf(testUserId)} disabled={isDownloading}>
 *     {isDownloading ? "Downloading..." : "Download PDF"}
 *   </button>
 *
 * Used in: IAmStatementsSummaryComponent.tsx
 */
export function useDownloadIAmPdf() {
  const mutation = useMutation({
    mutationFn: async (userId?: string) => {
      // Fetch the PDF blob from the API
      // If userId is provided, uses admin endpoint for that specific user
      const blob = await downloadIAmStatementsPdf(userId);

      // Create a download link and trigger the download
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "i-am-statements.pdf";
      document.body.appendChild(a);
      a.click();

      // Clean up
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },
  });

  return {
    downloadPdf: mutation.mutate,
    isDownloading: mutation.isPending,
    error: mutation.error,
  };
}
