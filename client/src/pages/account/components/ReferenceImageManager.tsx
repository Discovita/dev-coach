import { ReferenceImageUploader } from "./ReferenceImageUploader";

/**
 * ReferenceImageManager Component
 * -------------------------------
 * Account-page card wrapper around {@link ReferenceImageUploader}. The upload
 * behavior, grid, and guidance all live in the uploader; this just supplies the
 * card chrome used on the account page.
 *
 * @param userId - Optional user ID for admin impersonation. When provided,
 *                 fetches the target user's reference images via admin endpoints.
 *
 * Used in: Account page for managing reference images for AI image generation.
 */
export function ReferenceImageManager({ userId }: { userId?: string } = {}) {
	return (
		<div className="bg-card rounded-lg border p-6 space-y-4">
			<ReferenceImageUploader userId={userId} />
		</div>
	);
}
