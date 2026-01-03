import { useReferenceImages } from "@/hooks/use-reference-images";
import { ReferenceImageSlot } from "./ReferenceImageSlot";
import { ReferenceImage } from "@/types/referenceImage";
import { toast } from "sonner";

interface ReferenceImageManagerProps {
  /** User ID to manage reference images for */
  userId: string;
}

const MAX_REFERENCE_IMAGES = 5;

/**
 * ReferenceImageManager Component
 * -------------------------------
 * Manages up to 5 reference image slots for a user.
 * Displays slots in a grid, handles upload, replace, and delete operations.
 */
export function ReferenceImageManager({ userId }: ReferenceImageManagerProps) {
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
  const slots: (ReferenceImage | null)[] = Array(MAX_REFERENCE_IMAGES).fill(null);
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
        // Include user_id for admin users creating images for other users
        await createImage({
          data: { order: emptySlotIndex, user_id: userId },
          imageFile: file,
        });
        toast.success("Image uploaded successfully");
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Failed to upload image";
      toast.error(errorMessage);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteImage(id);
      toast.success("Image deleted successfully");
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Failed to delete image";
      toast.error(errorMessage);
    }
  };

  const isOperationInProgress = isCreating || isUploading || isDeleting;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Reference Images</h2>
        <p className="text-sm text-neutral-500">
          {referenceImages.length} / {MAX_REFERENCE_IMAGES} images uploaded
        </p>
      </div>

      <p className="text-sm text-neutral-600 dark:text-neutral-400">
        Upload up to 5 reference images of yourself. These will be used to generate identity images.
      </p>

      {isLoading ? (
        <div className="text-neutral-500 py-8 text-center">Loading reference images...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
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

