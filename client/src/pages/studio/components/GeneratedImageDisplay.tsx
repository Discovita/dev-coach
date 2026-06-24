import { Button } from "@/components/ui/button";
import type { Identity } from "@/types/identity";
import { Download, RefreshCw, Save } from "lucide-react";
import { toast } from "sonner";

interface GeneratedImageDisplayProps {
	/** Base64 encoded image data */
	imageBase64: string | null;
	/** Selected identity to save to */
	identity: Identity | null;
	/** Whether save is in progress */
	isSaving: boolean;
	/** Callback when save button is clicked */
	onSave: (identityId: string, imageBase64: string) => Promise<void>;
	/**
	 * When true, this component renders without the outer card/title styling.
	 * Useful when the parent layout provides the container (e.g. a "studio" panel).
	 */
	embedded?: boolean;
	/**
	 * Optional title shown above the image when not embedded.
	 * Set to null to hide.
	 */
	title?: string | null;
}

/**
 * GeneratedImageDisplay Component
 * --------------------------------
 * Displays a generated identity image with options to save, download, or regenerate.
 */
export function GeneratedImageDisplay({
	imageBase64,
	identity,
	isSaving,
	onSave,
	embedded = false,
	title = "Generated Image",
}: GeneratedImageDisplayProps) {
	const handleDownload = () => {
		if (!imageBase64) return;

		try {
			// Convert base64 to blob
			const byteCharacters = atob(imageBase64);
			const byteNumbers = new Array(byteCharacters.length);
			for (let i = 0; i < byteCharacters.length; i++) {
				byteNumbers[i] = byteCharacters.charCodeAt(i);
			}
			const byteArray = new Uint8Array(byteNumbers);
			const blob = new Blob([byteArray], { type: "image/png" });

			// Create download link
			const url = URL.createObjectURL(blob);
			const link = document.createElement("a");
			link.href = url;
			link.download = `identity-image-${identity?.name || "generated"}-${Date.now()}.png`;
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
			URL.revokeObjectURL(url);

			toast.success("Image downloaded successfully");
		} catch (error) {
			toast.error("Failed to download image");
			console.error("Download error:", error);
		}
	};

	const handleSave = async () => {
		if (!imageBase64 || !identity?.id) {
			toast.error("No image or identity selected");
			return;
		}

		// Toast notifications for API success/error are handled by the useImageGeneration hook
		await onSave(identity.id, imageBase64);
	};

	if (!imageBase64) {
		return null;
	}

	const imageUrl = `data:image/png;base64,${imageBase64}`;

	const content = (
		<>
			<div className="flex items-center justify-center bg-[var(--nv-lilac-white)] rounded-lg p-4 mb-4 min-h-[400px]">
				<img
					src={imageUrl}
					alt="Generated identity"
					className="max-w-full max-h-[600px] object-contain rounded"
				/>
			</div>

			<div className="flex flex-wrap gap-2">
				<Button
					type="button"
					variant="default"
					onClick={handleSave}
					disabled={!identity?.id || isSaving}
					className="bg-[var(--nv-royal-purple)] hover:bg-[var(--nv-royal-purple)]/90"
				>
					{isSaving ? (
						<>
							<RefreshCw className="size-4 animate-spin" />
							Saving...
						</>
					) : (
						<>
							<Save className="size-4" />
							Save to Identity
						</>
					)}
				</Button>

				<Button
					type="button"
					variant="outline"
					onClick={handleDownload}
					disabled={!imageBase64}
					className="border-[var(--nv-royal-purple)]/30 text-[var(--nv-royal-purple)] hover:bg-[var(--nv-pale-lavender)]"
				>
					<Download className="size-4" />
					Download
				</Button>
			</div>
		</>
	);

	if (embedded) {
		return <div className="w-full">{content}</div>;
	}

	return (
		<div className="flex flex-col gap-4">
			{title !== null && (
				<h2 className="text-2xl font-semibold text-[var(--nv-indigo)]">
					{title}
				</h2>
			)}

			<div className="border border-[var(--nv-royal-purple)]/20 rounded-lg p-4 bg-[var(--nv-pale-lavender)]/30">
				{content}
			</div>
		</div>
	);
}
