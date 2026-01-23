import { useState, useEffect } from "react";
import { UserSelector } from "./components/UserSelector";
import { ReferenceImageManager } from "./components/ReferenceImageManager";
import { IdentitySelector } from "./components/IdentitySelector";
import { GeneratedImageDisplay } from "./components/GeneratedImageDisplay";
import { AppearanceSelector } from "./components/appearance/AppearanceSelector";
import { SceneInputs } from "./components/SceneInputs";
import { useProfile } from "@/hooks/use-profile";
import { useImageGeneration } from "@/hooks/use-image-generation";
import { useIdentities } from "@/hooks/use-identities";
import { useTestScenarioUserIdentities } from "@/hooks/test-scenario/use-test-scenario-user-identities";
import { useReferenceImages } from "@/hooks/use-reference-images";
import { useUserAppearance } from "@/hooks/use-user-appearance";
import { updateIdentity, adminUpdateIdentity } from "@/api/identities";
import { useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Identity } from "@/types/identity";
import { SceneInputs as SceneInputsType } from "@/types/sceneInputs";
import { UserAppearance } from "@/types/userAppearance";
import { toast } from "sonner";
import { Sparkles } from "lucide-react";

/**
 * Images Page
 * -----------
 * Admin-only page for generating identity images.
 * Allows admins to:
 * 1. Select a user (self or test account)
 * 2. Manage reference images for that user
 * 3. Select an identity
 * 4. Generate and save identity images
 */
export default function Images() {
  const { profile } = useProfile();
  const queryClient = useQueryClient();
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [selectedIdentityId, setSelectedIdentityId] = useState<string | null>(null);
  const [additionalPrompt, setAdditionalPrompt] = useState("");
  const [generatedImageBase64, setGeneratedImageBase64] = useState<string | null>(null);
  
  // Appearance state (loaded from user profile)
  const {
    appearance,
    isLoading: isLoadingAppearance,
    updateAppearance,
    isUpdating: isUpdatingAppearance,
  } = useUserAppearance(selectedUserId);
  
  // Scene inputs state (loaded from selected identity)
  const [sceneInputs, setSceneInputs] = useState<SceneInputsType>({
    clothing: "",
    mood: "",
    setting: "",
  });
  
  // Track if scene is being saved
  const [isSavingScene, setIsSavingScene] = useState(false);

  const {
    generateImage,
    saveImage,
    isGenerating,
    isSaving,
    generateData,
    startChat,
    continueChat,
    isStartingChat,
    isContinuingChat,
    startChatData,
    continueChatData,
  } = useImageGeneration();
  
  const [editPrompt, setEditPrompt] = useState("");

  // Fetch identities to get the selected identity object
  const { identities: currentUserIdentities } = useIdentities();
  const { identities: testUserIdentities } = useTestScenarioUserIdentities(
    selectedUserId || ""
  );
  const { referenceImages } = useReferenceImages(selectedUserId || undefined);
  const isCurrentUser = profile && selectedUserId === profile.id;
  const identities = isCurrentUser ? currentUserIdentities : testUserIdentities;
  const selectedIdentity = identities?.find(
    (id: Identity) => id.id === selectedIdentityId
  ) || null;

  // Check if user has reference images with actual image files
  const hasReferenceImages = referenceImages.some(
    (img) => img.image !== null && img.image !== undefined
  );

  // Set profile as default when it loads
  useEffect(() => {
    if (profile && !selectedUserId) {
      setSelectedUserId(profile.id);
    }
  }, [profile, selectedUserId]);

  // Reset selected identity when user changes
  useEffect(() => {
    setSelectedIdentityId(null);
    setGeneratedImageBase64(null);
  }, [selectedUserId]);

  // Clear generated image when identity changes
  useEffect(() => {
    setGeneratedImageBase64(null);
  }, [selectedIdentityId]);

  // Load scene inputs from selected identity when it changes
  useEffect(() => {
    if (selectedIdentity) {
      setSceneInputs({
        clothing: selectedIdentity.clothing || "",
        mood: selectedIdentity.mood || "",
        setting: selectedIdentity.setting || "",
      });
    } else {
      setSceneInputs({
        clothing: "",
        mood: "",
        setting: "",
      });
    }
  }, [selectedIdentity]);

  // Update generated image when generation completes
  useEffect(() => {
    if (generateData?.image_base64) {
      setGeneratedImageBase64(generateData.image_base64);
    }
  }, [generateData]);

  // Update generated image when chat starts
  useEffect(() => {
    if (startChatData?.image_base64) {
      setGeneratedImageBase64(startChatData.image_base64);
      setEditPrompt(""); // Clear edit prompt when starting new chat
    }
  }, [startChatData]);

  // Update generated image when chat continues
  useEffect(() => {
    if (continueChatData?.image_base64) {
      setGeneratedImageBase64(continueChatData.image_base64);
      setEditPrompt(""); // Clear edit prompt after successful edit
    }
  }, [continueChatData]);

  // Handle scene save - called when user clicks "Save Scene Details" button
  // Uses admin endpoint for test user identities, regular endpoint for own identities
  const handleSceneSave = async () => {
    if (!selectedIdentityId) {
      toast.error("Please select an identity first");
      return;
    }
    
    setIsSavingScene(true);
    try {
      const updateData = {
        clothing: sceneInputs.clothing || null,
        mood: sceneInputs.mood || null,
        setting: sceneInputs.setting || null,
      };
      
      // Use admin endpoint for test user identities, regular endpoint for own identities
      if (isCurrentUser) {
        await updateIdentity(selectedIdentityId, updateData);
      } else {
        await adminUpdateIdentity(selectedIdentityId, updateData);
      }
      
      // Invalidate identities queries to refresh
      queryClient.invalidateQueries({ queryKey: ["user", "identities"] });
      if (selectedUserId) {
        queryClient.invalidateQueries({ queryKey: ["testScenarioUser", selectedUserId, "identities"] });
      }
      toast.success("Scene details saved");
    } catch (error) {
      toast.error("Failed to save scene details");
      console.error("Failed to save scene inputs:", error);
      throw error; // Re-throw so SceneInputs knows save failed
    } finally {
      setIsSavingScene(false);
    }
  };

  // Handle appearance save - called when user clicks "Save Preferences" button
  const handleAppearanceSave = async (newAppearance: UserAppearance) => {
    if (!selectedUserId) return;
    
    try {
      await updateAppearance(newAppearance);
      toast.success("Appearance preferences saved");
    } catch (error) {
      toast.error("Failed to save appearance preferences");
      console.error("Appearance update error:", error);
      throw error; // Re-throw so AppearanceSelector knows save failed
    }
  };

  const handleGenerate = async () => {
    if (!selectedUserId || !selectedIdentityId) {
      toast.error("Please select a user and an identity");
      return;
    }

    if (!hasReferenceImages) {
      toast.error("Please upload at least one reference image before generating");
      return;
    }

    // Check if scene details have unsaved changes
    const sceneIsDirty = selectedIdentity && (
      sceneInputs.clothing !== (selectedIdentity.clothing || "") ||
      sceneInputs.mood !== (selectedIdentity.mood || "") ||
      sceneInputs.setting !== (selectedIdentity.setting || "")
    );

    if (sceneIsDirty) {
      toast.error("Please save scene details before generating an image");
      return;
    }

    try {
      // Use admin endpoint for test users, public endpoint for current user
      await startChat({
        identity_id: selectedIdentityId,
        ...(isCurrentUser ? {} : { user_id: selectedUserId }),
        additional_prompt: additionalPrompt.trim() || undefined,
      });
    } catch (error) {
      // Error is handled by the useImageGeneration hook
      console.error("Generation error:", error);
    }
  };

  const handleEdit = async () => {
    if (!selectedUserId) {
      toast.error("Please select a user");
      return;
    }

    if (!editPrompt.trim()) {
      toast.error("Please enter an edit instruction");
      return;
    }

    try {
      // Use admin endpoint for test users, public endpoint for current user
      await continueChat({
        ...(isCurrentUser ? {} : { user_id: selectedUserId }),
        edit_prompt: editPrompt.trim(),
      });
    } catch (error) {
      // Error is handled by the useImageGeneration hook
      console.error("Edit error:", error);
    }
  };

  const handleSave = async (identityId: string, imageBase64: string) => {
    await saveImage({
      identity_id: identityId,
      image_base64: imageBase64,
    });
    // Invalidate identities query to refresh the identity with new image
    // This is handled by the hook's query invalidation
  };

  const handleRegenerate = () => {
    // Regenerate calls handleGenerate which now uses startChat
    handleGenerate();
  };

  // Check if scene details have unsaved changes
  const sceneIsDirty = selectedIdentity && (
    sceneInputs.clothing !== (selectedIdentity.clothing || "") ||
    sceneInputs.mood !== (selectedIdentity.mood || "") ||
    sceneInputs.setting !== (selectedIdentity.setting || "")
  );

  const canGenerate =
    selectedUserId &&
    selectedIdentityId &&
    hasReferenceImages &&
    !isStartingChat &&
    !isGenerating &&
    !sceneIsDirty; // Must save scene details first

  const canEdit =
    selectedUserId &&
    generatedImageBase64 &&
    editPrompt.trim() &&
    !isContinuingChat;

  return (
    <div className="flex flex-col h-full w-full p-6 overflow-y-auto">
      <h1 className="text-3xl font-bold mb-6">Identity Image Generation</h1>

      <div className="mb-6">
        <UserSelector
          selectedUserId={selectedUserId}
          onUserSelect={setSelectedUserId}
        />
      </div>

      {selectedUserId && (
        <div className="flex-1 min-h-0 space-y-8">
          <ReferenceImageManager userId={selectedUserId} />

          {/* Appearance Selection Section (from User model) */}
          {!isLoadingAppearance && (
            <AppearanceSelector
              appearance={appearance}
              onSave={handleAppearanceSave}
              isSaving={isUpdatingAppearance}
            />
          )}

          <div className="space-y-4">
            <IdentitySelector
              selectedUserId={selectedUserId}
              selectedIdentityId={selectedIdentityId}
              onIdentitySelect={setSelectedIdentityId}
            />

            {selectedIdentityId && (
              <>
                {/* Scene Inputs Section (from/to Identity model) */}
                <SceneInputs
                  values={sceneInputs}
                  savedValues={selectedIdentity ? {
                    clothing: selectedIdentity.clothing || "",
                    mood: selectedIdentity.mood || "",
                    setting: selectedIdentity.setting || "",
                  } : { clothing: "", mood: "", setting: "" }}
                  onChange={setSceneInputs}
                  onSave={handleSceneSave}
                  isSaving={isSavingScene}
                  disabled={!selectedIdentityId}
                />

                {!hasReferenceImages && (
                  <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                    <p className="text-sm text-yellow-800 dark:text-yellow-200">
                      ⚠️ Please upload at least one reference image above before generating an identity image.
                    </p>
                  </div>
                )}

                <div className="space-y-2">
                  <label htmlFor="additional-prompt" className="text-sm font-medium">
                    Additional Prompt (Optional)
                  </label>
                  <Textarea
                    id="additional-prompt"
                    placeholder="Add any additional instructions for image generation..."
                    value={additionalPrompt}
                    onChange={(e) => setAdditionalPrompt(e.target.value)}
                    rows={3}
                    className="max-w-2xl"
                  />
                  <p className="text-xs text-neutral-500">
                    Optional: Add extra instructions to customize the generated image
                  </p>
                </div>

                <div className="space-y-2">
                  <Button
                    type="button"
                    variant="default"
                    onClick={handleGenerate}
                    disabled={!canGenerate || isUpdatingAppearance}
                    className="h-12 px-6 text-base"
                  >
                    {isStartingChat || isGenerating ? (
                      <>
                        <Sparkles className="size-5 animate-pulse" />
                        Generating Image...
                      </>
                    ) : (
                      <>
                        <Sparkles className="size-5" />
                        Generate New
                      </>
                    )}
                  </Button>

                  {sceneIsDirty && (
                    <p className="text-sm text-amber-600 dark:text-amber-400">
                      Save scene details before generating an image.
                    </p>
                  )}

                  {!hasReferenceImages && (
                    <p className="text-sm text-neutral-500">
                      Upload reference images above to enable image generation.
                    </p>
                  )}
                </div>
              </>
            )}
          </div>

          {generatedImageBase64 && selectedIdentity && (
            <>
              <GeneratedImageDisplay
                imageBase64={generatedImageBase64}
                identity={selectedIdentity}
                isGenerating={isGenerating || isStartingChat}
                isSaving={isSaving}
                onSave={handleSave}
                onRegenerate={handleRegenerate}
              />
              
              {/* Edit Image Section */}
              <div className="flex flex-col gap-4 border rounded-lg p-4 bg-neutral-50 dark:bg-neutral-900">
                <h2 className="text-xl font-semibold">Edit This Image</h2>
                <div className="space-y-2">
                  <label htmlFor="edit-prompt" className="text-sm font-medium">
                    Edit Instruction
                  </label>
                  <Textarea
                    id="edit-prompt"
                    placeholder="e.g., make the lighting warmer, change the background to a beach, add more vibrant colors..."
                    value={editPrompt}
                    onChange={(e) => setEditPrompt(e.target.value)}
                    rows={3}
                    className="max-w-2xl"
                  />
                  <p className="text-xs text-neutral-500">
                    Describe how you'd like to modify the current image
                  </p>
                </div>
                <div>
                  <Button
                    type="button"
                    variant="default"
                    onClick={handleEdit}
                    disabled={!canEdit}
                    className="h-10 px-6"
                  >
                    {isContinuingChat ? (
                      <>
                        <Sparkles className="size-4 animate-pulse" />
                        Applying Edit...
                      </>
                    ) : (
                      <>
                        <Sparkles className="size-4" />
                        Apply Edit
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {!selectedUserId && (
        <div className="flex-1 flex items-center justify-center text-neutral-500">
          Select a user to begin generating identity images
        </div>
      )}
    </div>
  );
}

