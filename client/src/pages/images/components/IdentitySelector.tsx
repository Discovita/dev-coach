import { useProfile } from "@/hooks/use-profile";
import { useIdentities } from "@/hooks/use-identities";
import { useTestScenarioUserIdentities } from "@/hooks/test-scenario/use-test-scenario-user-identities";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
  SelectGroup,
  SelectLabel,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import { Identity } from "@/types/identity";
import { toast } from "sonner";

interface IdentitySelectorProps {
  selectedUserId: string | null;
  selectedIdentityId: string | null;
  onIdentitySelect: (identityId: string | null) => void;
}

/**
 * IdentitySelector Component
 * --------------------------
 * Allows selecting an identity from the selected user's identities.
 * Handles both current user and test user identities.
 */
export function IdentitySelector({
  selectedUserId,
  selectedIdentityId,
  onIdentitySelect,
}: IdentitySelectorProps) {
  const { profile } = useProfile();
  const isCurrentUser = profile && selectedUserId === profile.id;

  // Fetch identities based on user type
  const {
    identities: currentUserIdentities,
    isLoading: isLoadingCurrent,
  } = useIdentities();

  const {
    identities: testUserIdentities,
    isLoading: isLoadingTest,
  } = useTestScenarioUserIdentities(selectedUserId || "");

  const identities = isCurrentUser ? currentUserIdentities : testUserIdentities;
  const isLoading = isCurrentUser ? isLoadingCurrent : isLoadingTest;

  const handleValueChange = (value: string) => {
    if (value === "none") {
      onIdentitySelect(null);
    } else {
      onIdentitySelect(value);
    }
  };

  const handleDownload = async () => {
    if (!selectedIdentity?.image?.original) {
      toast.error("No image available to download");
      return;
    }

    try {
      // Fetch the original image directly with CORS mode
      const response = await fetch(selectedIdentity.image.original, {
        mode: 'cors',
        credentials: 'omit'
      });
      if (!response.ok) {
        throw new Error("Failed to fetch image");
      }

      // Convert to blob
      const blob = await response.blob();

      // Create download link
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `identity-image-${selectedIdentity.name || "identity"}-${Date.now()}.png`;
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

  if (!selectedUserId) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="text-neutral-500">Loading identities...</div>
    );
  }

  if (!identities || identities.length === 0) {
    return (
      <div className="text-neutral-500">
        No identities found for this user. Create identities first.
      </div>
    );
  }

  const selectedIdentity = identities.find(
    (id: Identity) => id.id === selectedIdentityId
  );

  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium">Select Identity</label>
      <Select
        value={selectedIdentityId || "none"}
        onValueChange={handleValueChange}
      >
        <SelectTrigger className="w-full max-w-2xl h-12 text-base">
          <SelectValue placeholder="Choose an identity">
            {selectedIdentity
              ? `${selectedIdentity.name}${selectedIdentity.category ? ` (${selectedIdentity.category})` : ""}`
              : "Choose an identity"}
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectLabel>Identities</SelectLabel>
            <SelectItem value="none">None (Select an identity)</SelectItem>
            {identities.map((identity: Identity) => (
              <SelectItem key={identity.id} value={identity.id || ""}>
                {identity.name}
                {identity.category && ` (${identity.category})`}
              </SelectItem>
            ))}
          </SelectGroup>
        </SelectContent>
      </Select>

      {selectedIdentity && (
        <div className="mt-4 p-6 bg-neutral-50 dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800">
          {/* Two-column layout: image on left, details on right */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left side: Image */}
            <div className="flex flex-col items-center w-full">
              {(selectedIdentity.image?.original || selectedIdentity.image?.large || selectedIdentity.image?.medium || selectedIdentity.image?.thumbnail) ? (
                <>
                  <img
                    src={selectedIdentity.image.original || selectedIdentity.image.large || selectedIdentity.image.medium || selectedIdentity.image.thumbnail}
                    alt={`${selectedIdentity.name} identity image`}
                    className="w-full h-auto rounded-lg border border-neutral-300 dark:border-neutral-700"
                    style={{ minHeight: '300px', objectFit: 'contain', backgroundColor: '#f5f5f5' }}
                  />
                  <p className="text-sm text-neutral-500 mt-2">Current Image</p>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleDownload}
                    className="mt-2"
                  >
                    <Download className="size-4" />
                    Download
                  </Button>
                </>
              ) : (
                <div className="w-full aspect-video bg-neutral-200 dark:bg-neutral-800 rounded-lg flex items-center justify-center min-h-[300px]">
                  <p className="text-neutral-500 text-lg">No image generated yet</p>
                </div>
              )}
            </div>

            {/* Right side: Identity details */}
            <div className="flex flex-col justify-center">
              <h3 className="font-bold text-2xl mb-4">{selectedIdentity.name}</h3>
              {selectedIdentity.category && (
                <p className="text-base text-neutral-600 dark:text-neutral-400 mb-4">
                  <span className="font-semibold">Category:</span> {selectedIdentity.category}
                </p>
              )}
              {selectedIdentity.i_am_statement && (
                <p className="text-base text-neutral-600 dark:text-neutral-400 mb-4">
                  <span className="font-semibold">I Am:</span> {selectedIdentity.i_am_statement}
                </p>
              )}
              {selectedIdentity.visualization && (
                <p className="text-base text-neutral-600 dark:text-neutral-400">
                  <span className="font-semibold">Visualization:</span> {selectedIdentity.visualization}
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

