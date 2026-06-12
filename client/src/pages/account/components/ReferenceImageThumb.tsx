import { Loader2, Trash2 } from "lucide-react";

interface ReferenceImageThumbProps {
	/** URL of the image (server URL or local preview while uploading) */
	imageUrl?: string;
	/** Optional name/label for the image */
	name?: string;
	/** Number shown on the badge (1-5) */
	displayNumber: number;
	/** Whether this thumbnail is still uploading */
	isUploading?: boolean;
	/** Disables the remove button while another operation is in progress */
	isBusy?: boolean;
	/** Callback to remove this image (omitted for in-flight uploads) */
	onRemove?: () => void;
}

/**
 * ReferenceImageThumb Component
 * -----------------------------
 * A single thumbnail in the reference-photo grid. Shows the image (or a local
 * preview with a spinner while uploading) and a hover/focus remove button.
 *
 * Used in: ReferenceImageManager on the Account page.
 */
export function ReferenceImageThumb({
	imageUrl,
	name,
	displayNumber,
	isUploading,
	isBusy,
	onRemove,
}: ReferenceImageThumbProps) {
	return (
		<div className="group relative aspect-square rounded-lg overflow-hidden border border-[var(--nv-pale-lavender)] bg-[var(--nv-lilac-white)]">
			{/* Number badge */}
			<div className="absolute top-1.5 left-1.5 z-10 bg-[var(--nv-royal-purple)] text-white text-[10px] font-semibold px-1.5 py-0.5 rounded">
				{displayNumber}
			</div>

			{imageUrl && (
				<img
					src={imageUrl}
					alt={name || `Reference image ${displayNumber}`}
					className="w-full h-full object-cover"
				/>
			)}

			{isUploading ? (
				<div className="absolute inset-0 bg-black/40 flex items-center justify-center">
					<Loader2 className="size-6 text-white animate-spin" />
				</div>
			) : (
				onRemove && (
					<button
						type="button"
						onClick={onRemove}
						disabled={isBusy}
						aria-label={`Remove photo ${displayNumber}`}
						className="absolute top-1.5 right-1.5 z-10 rounded-full bg-black/60 text-white p-1 opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity hover:bg-black/80 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						<Trash2 className="size-3.5" />
					</button>
				)
			)}
		</div>
	);
}
