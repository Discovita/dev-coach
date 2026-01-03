import { Button } from "@/components/ui/button";
import { Download, Save, RefreshCw } from "lucide-react";
import { Identity } from "@/types/identity";
import { toast } from "sonner";

interface GeneratedImageDisplayProps {
  /** Base64 encoded image data */
  imageBase64: string | null;
  /** Selected identity to save to */
  identity: Identity | null;
  /** Whether generation is in progress */
  isGenerating: boolean;
  /** Whether save is in progress */
  isSaving: boolean;
  /** Callback when save button is clicked */
  onSave: (identityId: string, imageBase64: string) => Promise<void>;
  /** Callback when regenerate button is clicked */
  onRegenerate: () => void;
}

/**
 * GeneratedImageDisplay Component
 * --------------------------------
 * Displays a generated identity image with options to save, download, or regenerate.
 */
export function GeneratedImageDisplay({
  imageBase64,
  identity,
  isGenerating,
  isSaving,
  onSave,
  onRegenerate,
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

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-2xl font-semibold">Generated Image</h2>

      <div className="border rounded-lg p-4 bg-neutral-50 dark:bg-neutral-900">
        <div className="flex items-center justify-center bg-neutral-100 dark:bg-neutral-800 rounded-lg p-4 mb-4 min-h-[400px]">
          <img
            src={imageUrl}
            alt="Generated identity image"
            className="max-w-full max-h-[600px] object-contain rounded"
          />
        </div>

        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            variant="default"
            onClick={handleSave}
            disabled={!identity?.id || isSaving}
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
          >
            <Download className="size-4" />
            Download
          </Button>

          <Button
            type="button"
            variant="outline"
            onClick={onRegenerate}
            disabled={isGenerating}
          >
            {isGenerating ? (
              <>
                <RefreshCw className="size-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <RefreshCw className="size-4" />
                Regenerate
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

