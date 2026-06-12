import { Button } from "@/components/ui/button";
import { useReferenceImages } from "@/hooks/use-reference-images";
import type { ReferenceImage } from "@/types/referenceImage";
import { ImagePlus, Upload } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { ReferenceImageThumb } from "./ReferenceImageThumb";

const MAX_REFERENCE_IMAGES = 5;

/** A photo being uploaded right now — shown as a thumbnail with a spinner. */
interface PendingUpload {
	tempId: string;
	previewUrl: string;
	order: number;
}

/**
 * Resolve the thumbnail URL for a saved image. Prefers the 600px "large" size
 * (crisp without the full-res load cost) and cache-busts with updated_at so a
 * replaced image reloads.
 */
function serverImageUrl(img: ReferenceImage): string | undefined {
	const base = img.image?.large || img.image?.original || img.image?.medium;
	if (!base) return undefined;
	return img.updated_at
		? `${base}?t=${new Date(img.updated_at).getTime()}`
		: base;
}

/**
 * ReferenceImageManager Component
 * -------------------------------
 * Single upload area for up to 5 reference photos. Supports picking several
 * files at once and drag-and-drop. Uploaded (and in-flight) photos show as a
 * thumbnail grid; each finished photo can be removed.
 *
 * @param userId - Optional user ID for admin impersonation. When provided,
 *                 fetches the target user's reference images via admin endpoints.
 *
 * Used in: Account page for managing reference images for AI image generation.
 */
export function ReferenceImageManager({ userId }: { userId?: string } = {}) {
	const { referenceImages, isLoading, createImage, deleteImage, isDeleting } =
		useReferenceImages(userId);

	const fileInputRef = useRef<HTMLInputElement>(null);
	const [pending, setPending] = useState<PendingUpload[]>([]);
	const [isDragging, setIsDragging] = useState(false);
	// Tracks nested dragenter/dragleave so the highlight doesn't flicker over children.
	const dragDepth = useRef(0);

	const usedCount = referenceImages.length + pending.length;
	const isFull = usedCount >= MAX_REFERENCE_IMAGES;

	const uploadOne = async (file: File, order: number) => {
		const tempId = crypto.randomUUID();
		const previewUrl = URL.createObjectURL(file);
		setPending((prev) => [...prev, { tempId, previewUrl, order }]);
		try {
			await createImage({ data: { order }, imageFile: file });
			// On success, keep the preview on screen until the refetched list
			// actually contains this order (pruned by the effect below). This
			// avoids the thumbnail blinking out between upload and refetch.
		} catch (error) {
			setPending((prev) => prev.filter((p) => p.tempId !== tempId));
			URL.revokeObjectURL(previewUrl);
			const message =
				error instanceof Error ? error.message : "Failed to upload image";
			toast.error(`${file.name}: ${message}`);
		}
	};

	// Tracks pending uploads whose real thumbnail is already being preloaded,
	// so the effect below doesn't kick off the same preload twice.
	const preloading = useRef<Set<string>>(new Set());

	// When a saved image arrives for a pending upload, preload its real
	// thumbnail in the background and only drop the local preview once that
	// image has fully loaded. The preview (with spinner) stays put until then,
	// so the swap is instant from cache — no flash between preview and image.
	useEffect(() => {
		const byOrder = new Map(referenceImages.map((i) => [i.order, i]));
		for (const p of pending) {
			if (preloading.current.has(p.tempId)) continue;
			const img = byOrder.get(p.order);
			if (!img) continue;

			preloading.current.add(p.tempId);
			const finish = () => {
				preloading.current.delete(p.tempId);
				URL.revokeObjectURL(p.previewUrl);
				setPending((prev) => prev.filter((x) => x.tempId !== p.tempId));
			};

			const url = serverImageUrl(img);
			if (!url) {
				finish();
				continue;
			}
			const preloader = new Image();
			preloader.onload = finish;
			preloader.onerror = finish;
			preloader.src = url;
		}
	}, [referenceImages, pending]);

	const handleFiles = (fileList: FileList | null) => {
		if (!fileList || fileList.length === 0) return;

		const images = Array.from(fileList).filter((f) =>
			f.type.startsWith("image/"),
		);
		if (images.length === 0) {
			toast.error("Please choose image files only");
			return;
		}
		if (isFull) {
			toast.error(`Maximum ${MAX_REFERENCE_IMAGES} reference images allowed`);
			return;
		}

		// Reserve the lowest free slots (orders 0-4) for this batch up front so
		// concurrent uploads don't land on the same order.
		const usedOrders = new Set<number>([
			...referenceImages.map((i) => i.order),
			...pending.map((p) => p.order),
		]);
		const freeOrders: number[] = [];
		for (let o = 0; o < MAX_REFERENCE_IMAGES; o++) {
			if (!usedOrders.has(o)) freeOrders.push(o);
		}

		const accepted = images.slice(0, freeOrders.length);
		if (images.length > accepted.length) {
			toast.warning(
				`Only ${accepted.length} added — the limit is ${MAX_REFERENCE_IMAGES} photos`,
			);
		}

		accepted.forEach((file, i) => uploadOne(file, freeOrders[i]));
	};

	const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		handleFiles(e.target.files);
		// Reset so picking the same file again still fires onChange.
		if (fileInputRef.current) fileInputRef.current.value = "";
	};

	const handleDragEnter = (e: React.DragEvent) => {
		e.preventDefault();
		dragDepth.current += 1;
		setIsDragging(true);
	};

	const handleDragLeave = (e: React.DragEvent) => {
		e.preventDefault();
		dragDepth.current -= 1;
		if (dragDepth.current <= 0) {
			dragDepth.current = 0;
			setIsDragging(false);
		}
	};

	const handleDrop = (e: React.DragEvent) => {
		e.preventDefault();
		dragDepth.current = 0;
		setIsDragging(false);
		handleFiles(e.dataTransfer.files);
	};

	const handleDelete = async (id: string) => {
		try {
			await deleteImage(id);
			toast.success("Image deleted");
		} catch (error) {
			const message =
				error instanceof Error ? error.message : "Failed to delete image";
			toast.error(message);
		}
	};

	// Merge saved images and in-flight uploads into one list ordered by slot.
	// While a slot still has a pending preview, show that preview (not the saved
	// image) so the same slot never renders twice; the effect above swaps it for
	// the saved image once that image has finished preloading.
	const pendingOrders = new Set(pending.map((p) => p.order));
	const tiles = [
		...referenceImages
			.filter((img) => !pendingOrders.has(img.order))
			.map((img) => ({
				kind: "image" as const,
				order: img.order,
				img,
			})),
		...pending.map((p) => ({
			kind: "pending" as const,
			order: p.order,
			pending: p,
		})),
	].sort((a, b) => a.order - b.order);

	return (
		<div className="bg-card rounded-lg border p-6 space-y-4">
			<div className="flex items-center justify-between">
				<h2 className="text-xl font-medium">Reference Photos</h2>
				<p className="text-sm text-muted-foreground">
					{usedCount} / {MAX_REFERENCE_IMAGES} uploaded
				</p>
			</div>

			<p className="text-md text-muted-foreground">
				Upload up to 5 photos of yourself. These will be used to generate
				personalized identity images.
			</p>
			<div className="text-sm text-muted-foreground mt-[-10px]">
				<span>
					Note: For the best results, try to meet the following criteria:
				</span>
				<ul className="list-disc pl-6">
					<li>Be in a well-lit environment</li>
					<li>Upload at least 3 images</li>
					<li>
						Upload at least 1 photo with your mouth closed. The rest can be of
						your beautiful smile.
					</li>
					<li>Avoid photos with sunglasses or hats.</li>
					<li>
						Upload photos that have the hairstyle you'd like to see in your
						images. Maintain consistency across images.
					</li>
					<li>
						Upload photos that have the facial hair you'd like to see in your
						images. Maintain consistency across images.
					</li>
				</ul>
			</div>

			{isLoading ? (
				<div className="text-muted-foreground py-8 text-center">
					Loading reference images...
				</div>
			) : (
				<div
					onDragEnter={handleDragEnter}
					onDragOver={(e) => e.preventDefault()}
					onDragLeave={handleDragLeave}
					onDrop={handleDrop}
					className={`rounded-lg border-2 border-dashed p-4 transition-colors ${
						isDragging
							? "border-[var(--nv-royal-purple)] bg-[var(--nv-lilac-white)]"
							: "border-[var(--nv-pale-lavender)]"
					}`}
				>
					{tiles.length > 0 && (
						<div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 mb-4">
							{tiles.map((tile) => {
								if (tile.kind === "pending") {
									return (
										<ReferenceImageThumb
											key={tile.pending.tempId}
											imageUrl={tile.pending.previewUrl}
											displayNumber={tile.order + 1}
											isUploading
										/>
									);
								}
								const { img } = tile;
								const url = serverImageUrl(img);
								return (
									<ReferenceImageThumb
										key={img.id}
										imageUrl={url}
										name={img.name}
										displayNumber={img.order + 1}
										isBusy={isDeleting}
										onRemove={() => handleDelete(img.id)}
									/>
								);
							})}
						</div>
					)}

					<div className="flex flex-col items-center justify-center gap-2 py-6 text-center">
						<ImagePlus className="size-10 text-[var(--nv-pale-lavender)]" />
						{isFull ? (
							<p className="text-sm text-muted-foreground">
								You've reached the {MAX_REFERENCE_IMAGES}-photo limit. Remove
								one to add more.
							</p>
						) : (
							<>
								<p className="text-sm text-muted-foreground">
									Drag &amp; drop photos here, or
								</p>
								<Button
									type="button"
									onClick={() => fileInputRef.current?.click()}
									className="nv-gradient-button text-white"
								>
									<Upload className="size-4 mr-1" />
									Upload Photos
								</Button>
							</>
						)}
					</div>

					<input
						ref={fileInputRef}
						type="file"
						accept="image/*"
						multiple
						onChange={handleInputChange}
						className="hidden"
					/>
				</div>
			)}
		</div>
	);
}
