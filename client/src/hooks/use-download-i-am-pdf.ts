import { downloadIAmStatementsPdf } from "@/api/identities";
import { useUserTarget } from "@/context/UserTargetContext";
import { useMutation } from "@tanstack/react-query";

/**
 * useDownloadIAmPdf hook
 *
 * Handles downloading the I Am Statements PDF.
 * Uses TanStack Query's useMutation for managing loading state and errors.
 *
 * Resolves "whose PDF?" from UserTargetContext — the same source every
 * other data hook uses — so it works under both test scenarios and
 * global impersonation. When impersonating, it hits the admin endpoint
 * for the targeted user; otherwise the logged-in user's own endpoint.
 *
 * Step-by-step:
 * 1. Calls the downloadIAmStatementsPdf API function (admin endpoint when impersonating)
 * 2. Creates a Blob URL from the response
 * 3. Triggers browser download via hidden anchor element
 * 4. Cleans up the Blob URL after download
 *
 * Usage:
 *   const { downloadPdf, isDownloading, error } = useDownloadIAmPdf();
 *   <button onClick={() => downloadPdf()} disabled={isDownloading}>
 *     {isDownloading ? "Downloading..." : "Download PDF"}
 *   </button>
 *
 * Used in: IAmStatementsSummaryComponent.tsx
 */
export function useDownloadIAmPdf() {
	const { isImpersonating, targetUserId } = useUserTarget();
	const mutation = useMutation({
		mutationFn: async () => {
			// When impersonating (test scenario or global), hit the admin endpoint
			// for the targeted user; otherwise download the logged-in user's PDF.
			const blob = await downloadIAmStatementsPdf(
				isImpersonating ? (targetUserId ?? undefined) : undefined,
			);

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
