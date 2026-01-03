import { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { ReferenceImage } from "@/types/referenceImage";
import { Trash2, Upload, Image as ImageIcon } from "lucide-react";

interface ReferenceImageSlotProps {
  /** Slot number (0-4, displayed as 1-5) */
  slotNumber: number;
  /** Reference image data if exists, null if empty */
  referenceImage: ReferenceImage | null;
  /** Callback when image file is selected for upload */
  onUpload: (file: File, existingId?: string) => void;
  /** Callback when image should be deleted */
  onDelete: (id: string) => void;
  /** Whether an operation is in progress */
  isLoading: boolean;
}

/**
 * ReferenceImageSlot Component
 * ----------------------------
 * Displays a single reference image slot (1-5).
 * Shows image if exists, allows upload/replace, and delete.
 */
export function ReferenceImageSlot({
  slotNumber,
  referenceImage,
  onUpload,
  onDelete,
  isLoading,
}: ReferenceImageSlotProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onUpload(file, referenceImage?.id);
      // Reset input so same file can be selected again
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleDelete = () => {
    if (referenceImage?.id) {
      onDelete(referenceImage.id);
    }
  };

  const displayNumber = slotNumber + 1;
  const hasImage = referenceImage?.image !== null && referenceImage?.image !== undefined;
  const imageUrl = referenceImage?.image?.medium || referenceImage?.image?.thumbnail || referenceImage?.image?.original;

  return (
    <div
      className="relative border-2 border-dashed border-neutral-300 dark:border-neutral-700 rounded-lg p-4 min-h-[200px] flex flex-col items-center justify-center gap-2 bg-neutral-50 dark:bg-neutral-900 transition-colors"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Slot number badge */}
      <div className="absolute top-2 left-2 bg-gold-500 text-black text-xs font-semibold px-2 py-1 rounded">
        Slot {displayNumber}
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
        disabled={isLoading}
      />

      {/* Content area */}
      {hasImage && imageUrl ? (
        <>
          {/* Image preview */}
          <div className="relative w-full h-full flex items-center justify-center">
            <img
              src={imageUrl}
              alt={referenceImage?.name || `Reference image ${displayNumber}`}
              className="max-w-full max-h-[160px] object-contain rounded"
            />
            
            {/* Overlay buttons on hover */}
            {isHovered && (
              <div className="absolute inset-0 bg-black/50 rounded flex items-center justify-center gap-2">
                <Button
                  type="button"
                  variant="default"
                  size="sm"
                  onClick={handleUploadClick}
                  disabled={isLoading}
                >
                  <Upload className="size-4" />
                  Replace
                </Button>
                <Button
                  type="button"
                  variant="destructive"
                  size="sm"
                  onClick={handleDelete}
                  disabled={isLoading}
                >
                  <Trash2 className="size-4" />
                  Delete
                </Button>
              </div>
            )}
          </div>

          {/* Image name if exists */}
          {referenceImage?.name && (
            <p className="text-xs text-neutral-600 dark:text-neutral-400 truncate max-w-full">
              {referenceImage.name}
            </p>
          )}
        </>
      ) : (
        /* Empty slot - show upload button */
        <div className="flex flex-col items-center justify-center gap-2 text-neutral-500">
          <ImageIcon className="size-12" />
          <Button
            type="button"
            variant="default"
            onClick={handleUploadClick}
            disabled={isLoading}
          >
            <Upload className="size-4" />
            Upload Image
          </Button>
        </div>
      )}

      {/* Loading overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-black/30 rounded flex items-center justify-center">
          <div className="text-white text-sm">Processing...</div>
        </div>
      )}
    </div>
  );
}

