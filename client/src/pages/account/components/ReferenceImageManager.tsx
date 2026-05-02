import { useReferenceImages } from "@/hooks/use-reference-images";
import { ReferenceImageSlot } from "./ReferenceImageSlot";
import type { ReferenceImage } from "@/types/referenceImage";
import { toast } from "sonner";

const MAX_REFERENCE_IMAGES = 5;

/**
 * ReferenceImageManager Component
 * -------------------------------
 * Manages up to 5 reference image slots for a user.
 * Displays slots in a grid, handles upload, replace, and delete operations.
 *
 * @param userId - Optional user ID for admin impersonation. When provided,
 *                 fetches the target user's reference images via admin endpoints.
 *
 * Used in: Account page for managing reference images for AI image generation.
 */
export function ReferenceImageManager({ userId }: { userId?: string } = {}) {
  const {
    referenceImages,
    isLoading,
    createImage,
    uploadImage,
    deleteImage,
    isCreating,
    isUploading,
    isDeleting,
  } = useReferenceImages(userId);

  // Create array of 5 slots, filling with existing images by order
  const slots: (ReferenceImage | null)[] =
    Array(MAX_REFERENCE_IMAGES).fill(null);
  referenceImages.forEach((img) => {
    if (img.order >= 0 && img.order < MAX_REFERENCE_IMAGES) {
      slots[img.order] = img;
    }
  });

  const handleUpload = async (file: File, existingId?: string) => {
    try {
      if (existingId) {
        // Replace existing image
        await uploadImage({ id: existingId, imageFile: file });
        toast.success("Image replaced successfully");
      } else {
        // Find first empty slot
        const emptySlotIndex = slots.findIndex((slot) => slot === null);
        if (emptySlotIndex === -1) {
          toast.error("Maximum 5 reference images allowed");
          return;
        }

        // Create new reference image
        await createImage({
          data: { order: emptySlotIndex },
          imageFile: file,
        });
        toast.success("Image uploaded successfully");
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to upload image";
      toast.error(errorMessage);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteImage(id);
      toast.success("Image deleted successfully");
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to delete image";
      toast.error(errorMessage);
    }
  };

  const isOperationInProgress = isCreating || isUploading || isDeleting;

  return (
    <div className="bg-card rounded-lg border p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-medium">Reference Photos</h2>
        <p className="text-sm text-muted-foreground">
          {referenceImages.length} / {MAX_REFERENCE_IMAGES} uploaded
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
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {slots.map((referenceImage, index) => (
            <ReferenceImageSlot
              key={referenceImage?.id || `empty-${index}`}
              slotNumber={index}
              referenceImage={referenceImage}
              onUpload={handleUpload}
              onDelete={handleDelete}
              isLoading={isOperationInProgress}
            />
          ))}
        </div>
      )}
    </div>
  );
}
