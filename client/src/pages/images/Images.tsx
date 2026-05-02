import { useState, useEffect, useMemo } from "react";
import { IdentitySelector, SceneInputs, GeneratedImageDisplay, GenerationStatus } from "./components";
import { useIdentities } from "@/hooks/use-identities";
import { useImageGeneration, parseImageError } from "@/hooks/use-image-generation";
import { useReferenceImages } from "@/hooks/use-reference-images";
import { useUserTarget } from "@/context/UserTargetContext";
import { updateIdentity, adminUpdateIdentity } from "@/api/identities";
import { useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import type { Identity } from "@/types/identity";
import type { SceneInputs as SceneInputsType } from "@/types/sceneInputs";
import { toast } from "sonner";
import { Sparkles, AlertTriangle, Info, X, ChevronDown } from "lucide-react";
import { Link } from "@tanstack/react-router";
import {
  getIdentityCategoryColor,
  getIdentityCategoryDisplayName,
  getIdentityCategoryIcon,
} from "@/enums/identityCategory";
import { AnimatePresence, motion } from "framer-motion";

/**
 * Images Page
 * -----------
 * Page for generating identity images.
 * Allows users to:
 * 1. Select an identity
 * 2. Configure scene details (clothing, mood, setting)
 * 3. Generate and save identity images
 * 4. Edit generated images with follow-up prompts
 */
export default function Images() {
  const queryClient = useQueryClient();
  const { isImpersonating, targetUserId, queryKeyPrefix } = useUserTarget();
  const [selectedIdentityId, setSelectedIdentityId] = useState<string | null>(null);
  const [additionalPrompt, setAdditionalPrompt] = useState("");
  const [generatedImageBase64, setGeneratedImageBase64] = useState<string | null>(null);
  const [isCurrentIdentityImageOpen, setIsCurrentIdentityImageOpen] = useState(false);
  /**
   * Controls the "Advanced" section (animated open/close).
   * We keep this explicit (vs native <details>) so we can animate height nicely.
   */
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);
  
  // Scene inputs state (loaded from selected identity)
  const [sceneInputs, setSceneInputs] = useState<SceneInputsType>({
    clothing: "",
    mood: "",
    setting: "",
  });
  
  // Track if scene is being saved
  const [isSavingScene, setIsSavingScene] = useState(false);

  const {
    saveImage,
    isSaving,
    startChat,
    continueChat,
    isStartingChat,
    isContinuingChat,
    startChatData,
    continueChatData,
    startChatError,
    continueChatError,
    resetStartChat,
    resetContinueChat,
  } = useImageGeneration();
  
  const [editPrompt, setEditPrompt] = useState("");

  // Fetch identities — useIdentities already reads UserTargetContext
  const { identities } = useIdentities();
  // When impersonating, check the target user's reference images
  const { referenceImages } = useReferenceImages(
    isImpersonating ? targetUserId ?? undefined : undefined
  );
  
  const selectedIdentity = identities?.find(
    (id: Identity) => id.id === selectedIdentityId
  ) || null;

  /**
   * Best-available URLs for the currently-selected identity's existing image.
   * - Thumbnail: prefer smaller renditions for fast, compact display.
   * - Full: prefer the largest rendition so the lightbox can render big.
   */
  const currentIdentityThumbUrl =
    selectedIdentity?.image?.large ||
    selectedIdentity?.image?.medium ||
    selectedIdentity?.image?.original ||
    selectedIdentity?.image?.thumbnail ||
    null;

  const currentIdentityFullUrl =
    selectedIdentity?.image?.original ||
    selectedIdentity?.image?.large ||
    selectedIdentity?.image?.medium ||
    selectedIdentity?.image?.thumbnail ||
    null;

  // Check if user has reference images with actual image files
  const hasReferenceImages = referenceImages.some(
    (img) => img.image !== null && img.image !== undefined
  );

  // Parse errors for display - separate for generate and edit sections
  const generateError = useMemo(() => {
    return parseImageError(startChatError);
  }, [startChatError]);

  const editError = useMemo(() => {
    return parseImageError(continueChatError);
  }, [continueChatError]);

  // Handlers to dismiss errors
  const handleDismissGenerateError = () => {
    resetStartChat();
  };

  const handleDismissEditError = () => {
    resetContinueChat();
  };

  // Clear generated image when identity changes
  useEffect(() => {
    setGeneratedImageBase64(null);
    setEditPrompt("");
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

  // Handle scene save — uses admin endpoint when impersonating another user
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
      
      if (isImpersonating) {
        await adminUpdateIdentity(selectedIdentityId, updateData);
      } else {
        await updateIdentity(selectedIdentityId, updateData);
      }
      
      queryClient.invalidateQueries({ queryKey: [...queryKeyPrefix, "identities"] });
      toast.success("Scene details saved");
    } catch (error) {
      toast.error("Failed to save scene details");
      console.error("Failed to save scene inputs:", error);
      throw error;
    } finally {
      setIsSavingScene(false);
    }
  };

  const handleGenerate = async () => {
    if (!selectedIdentityId) {
      toast.error("Please select an identity");
      return;
    }

    if (!hasReferenceImages) {
      toast.error("Please upload at least one reference image in your Account settings before generating");
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
      await startChat({
        identity_id: selectedIdentityId,
        ...(isImpersonating && targetUserId ? { user_id: targetUserId } : {}),
        additional_prompt: additionalPrompt.trim() || undefined,
      });
    } catch (error) {
      console.error("Generation error:", error);
    }
  };

  const handleEdit = async () => {
    if (!editPrompt.trim()) {
      toast.error("Please enter an edit instruction");
      return;
    }

    try {
      await continueChat({
        ...(isImpersonating && targetUserId ? { user_id: targetUserId } : {}),
        edit_prompt: editPrompt.trim(),
      });
    } catch (error) {
      console.error("Edit error:", error);
    }
  };

  const handleSave = async (identityId: string, imageBase64: string) => {
    await saveImage({
      identity_id: identityId,
      image_base64: imageBase64,
      admin: isImpersonating,
    });
  };

  // Check if scene details have unsaved changes
  const sceneIsDirty = selectedIdentity && (
    sceneInputs.clothing !== (selectedIdentity.clothing || "") ||
    sceneInputs.mood !== (selectedIdentity.mood || "") ||
    sceneInputs.setting !== (selectedIdentity.setting || "")
  );

  const canGenerate =
    selectedIdentityId &&
    hasReferenceImages &&
    !isStartingChat &&
    !sceneIsDirty; // Must save scene details first

  const canEdit =
    generatedImageBase64 &&
    editPrompt.trim() &&
    !isContinuingChat;

  /**
   * Lightbox behavior for previewing the existing identity image.
   * This avoids introducing a new modal dependency while still allowing a larger view.
   */
  useEffect(() => {
    if (!isCurrentIdentityImageOpen) return;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsCurrentIdentityImageOpen(false);
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [isCurrentIdentityImageOpen]);

  return (
    <div className="flex flex-col h-full w-full overflow-y-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-[var(--nv-indigo)]">Identity Image Studio</h1>
        <p className="text-sm text-[var(--nv-royal-purple)]/70 mt-2 max-w-3xl">
          Pick an identity, describe the scene, generate a draft, then refine it with edits.
        </p>
      </div>

      <div className="flex-1 min-h-0">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left column: Inputs */}
          <div className="lg:col-span-5 xl:col-span-4 space-y-6">
            {/* Reference Images Warning */}
            {!hasReferenceImages && (
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg flex items-start gap-3">
                <AlertTriangle className="size-5 text-amber-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-amber-800">
                    Reference images required
                  </p>
                  <p className="text-sm text-amber-700 mt-1">
                    Please upload at least one reference image in{" "}
                    <Link
                      to="/account"
                      className="underline hover:text-amber-900 font-medium"
                    >
                      {isImpersonating ? "their Account settings" : "your Account settings"}
                    </Link>{" "}
                    before generating identity images.
                  </p>
                </div>
              </div>
            )}

            <div className="p-4 border border-[var(--nv-royal-purple)]/20 rounded-lg bg-[var(--nv-pale-lavender)]/20 space-y-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold text-[var(--nv-indigo)]">Setup</h2>
                  <p className="text-xs text-[var(--nv-royal-purple)]/60 mt-1">
                    Choose an identity and set the scene.
                  </p>
                </div>
                <Info className="size-4 text-[var(--nv-royal-purple)]/60 mt-1 flex-shrink-0" />
              </div>

              <IdentitySelector
                selectedIdentityId={selectedIdentityId}
                onIdentitySelect={setSelectedIdentityId}
                showSelectedIdentityCard={false}
              />
            </div>

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

                {/* Advanced options (animated slide-down) */}
                <div className="border border-[var(--nv-royal-purple)]/20 rounded-lg bg-[var(--nv-pale-lavender)]/20">
                  <button
                    type="button"
                    className="w-full flex items-center justify-between gap-3 p-4 cursor-pointer select-none text-sm font-medium text-[var(--nv-indigo)]"
                    aria-expanded={isAdvancedOpen}
                    aria-controls="images-advanced-options"
                    onClick={() => setIsAdvancedOpen((v) => !v)}
                  >
                    <span>Advanced (optional)</span>
                    <ChevronDown
                      className={`size-4 text-[var(--nv-royal-purple)]/70 transition-transform duration-200 ${
                        isAdvancedOpen ? "rotate-180" : ""
                      }`}
                    />
                  </button>

                  <AnimatePresence initial={false}>
                    {isAdvancedOpen && (
                      <motion.div
                        key="advanced-options"
                        id="images-advanced-options"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2, ease: "easeInOut" }}
                        className="overflow-hidden"
                      >
                        <div className="px-4 pb-4 space-y-2">
                          <label
                            htmlFor="additional-prompt"
                            className="text-sm font-medium text-[var(--nv-indigo)]"
                          >
                            Additional Prompt
                          </label>
                          <Textarea
                            id="additional-prompt"
                            placeholder="Add any additional instructions for image generation..."
                            value={additionalPrompt}
                            onChange={(e) => setAdditionalPrompt(e.target.value)}
                            rows={3}
                            className="w-full border-[var(--nv-royal-purple)]/30 focus:ring-[var(--nv-royal-purple)]"
                          />
                          <p className="text-xs text-[var(--nv-royal-purple)]/60">
                            Extra instructions to customize the generated image.
                          </p>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {/* Current identity snapshot (compact) */}
                {selectedIdentity && currentIdentityThumbUrl && (
                  <div className="border border-[var(--nv-royal-purple)]/20 rounded-lg bg-[var(--nv-pale-lavender)]/20 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <h3 className="text-sm font-semibold text-[var(--nv-indigo)]">
                          Current identity
                        </h3>
                        <p className="text-xs text-[var(--nv-royal-purple)]/60 mt-1">
                          Existing identity image + details.
                        </p>
                      </div>

                      {selectedIdentity.category &&
                        (() => {
                          const IconComponent = getIdentityCategoryIcon(
                            String(selectedIdentity.category)
                          );
                          const colorClasses = getIdentityCategoryColor(
                            String(selectedIdentity.category)
                          );
                          return (
                            <span
                              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${colorClasses} flex-shrink-0`}
                            >
                              <IconComponent className="w-3 h-3" />
                              <span>
                                {getIdentityCategoryDisplayName(
                                  String(selectedIdentity.category)
                                )}
                              </span>
                            </span>
                          );
                        })()}
                    </div>

                    <div className="mt-3 space-y-3">
                      <div className="text-sm text-[var(--nv-indigo)] font-medium truncate">
                        {selectedIdentity.name}
                      </div>

                      <button
                        type="button"
                        onClick={() => {
                          setIsCurrentIdentityImageOpen(true);
                        }}
                        className="w-full text-left disabled:cursor-not-allowed"
                        aria-label={
                          "Open current identity image"
                        }
                      >
                        <div className="w-full aspect-video rounded-lg overflow-hidden border border-[var(--nv-royal-purple)]/20 bg-[var(--nv-lilac-white)]">
                          <img
                            src={currentIdentityThumbUrl}
                            alt={`${selectedIdentity.name} current identity image`}
                            className="w-full h-full object-contain"
                            loading="lazy"
                          />
                        </div>
                        <p className="text-xs text-[var(--nv-royal-purple)]/60 mt-2">
                          Click to view larger
                        </p>
                      </button>

                      {selectedIdentity.i_am_statement && (
                        <p className="text-xs text-[var(--nv-royal-purple)]/80 line-clamp-3">
                          <span className="font-semibold text-[var(--nv-indigo)]">
                            I Am:
                          </span>{" "}
                          {selectedIdentity.i_am_statement}
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Right column: Preview + actions (sticky on desktop) */}
          <div className="lg:col-span-7 xl:col-span-8 space-y-6 lg:sticky lg:top-6 self-start">
            <div className="border border-[var(--nv-royal-purple)]/20 rounded-lg bg-[var(--nv-pale-lavender)]/30 p-4">
              <div className="flex flex-col gap-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <h2 className="text-xl font-semibold text-[var(--nv-indigo)]">Preview</h2>
                    {selectedIdentity ? (
                      <div className="mt-1 flex items-center gap-2 flex-wrap">
                        <p className="text-sm text-[var(--nv-royal-purple)]/70 truncate">
                          {selectedIdentity.name}
                        </p>
                        {selectedIdentity.category &&
                          (() => {
                            const IconComponent = getIdentityCategoryIcon(
                              String(selectedIdentity.category)
                            );
                            const colorClasses = getIdentityCategoryColor(
                              String(selectedIdentity.category)
                            );
                            return (
                              <span
                                className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${colorClasses}`}
                              >
                                <IconComponent className="w-3 h-3" />
                                <span>
                                  {getIdentityCategoryDisplayName(
                                    String(selectedIdentity.category)
                                  )}
                                </span>
                              </span>
                            );
                          })()}
                      </div>
                    ) : (
                      <p className="text-sm text-[var(--nv-royal-purple)]/60 mt-1">
                        Select an identity to begin.
                      </p>
                    )}
                  </div>

                  <div className="flex flex-col items-end gap-2 flex-shrink-0">
                    <Button
                      type="button"
                      variant="default"
                      onClick={handleGenerate}
                      disabled={!canGenerate}
                      className="h-11 px-5 bg-[var(--nv-royal-purple)] hover:bg-[var(--nv-royal-purple)]/90"
                    >
                      <Sparkles className="size-5" />
                      Generate
                    </Button>

                    <div className="w-full max-w-[320px]">
                      <GenerationStatus
                        isLoading={isStartingChat}
                        error={generateError}
                        onDismissError={handleDismissGenerateError}
                      />
                    </div>
                  </div>
                </div>

                {selectedIdentityId && sceneIsDirty && (
                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
                    <p className="text-sm text-amber-800 font-medium">
                      Save scene details before generating.
                    </p>
                    <p className="text-xs text-amber-700 mt-1">
                      Your scene inputs changed and haven’t been saved to this identity yet.
                    </p>
                  </div>
                )}

                {selectedIdentityId && !hasReferenceImages && (
                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
                    <p className="text-sm text-amber-800 font-medium">
                      Upload reference images to enable generation.
                    </p>
                    <p className="text-xs text-amber-700 mt-1">
                      Add them in Account settings, then come back here to generate.
                    </p>
                  </div>
                )}

                {/* Preview body */}
                {generatedImageBase64 && selectedIdentity ? (
                  <GeneratedImageDisplay
                    embedded
                    title={null}
                    imageBase64={generatedImageBase64}
                    identity={selectedIdentity}
                    isSaving={isSaving}
                    onSave={handleSave}
                  />
                ) : (
                  <div className="flex items-center justify-center bg-[var(--nv-lilac-white)] rounded-lg p-6 min-h-[420px] border border-[var(--nv-royal-purple)]/20">
                    <div className="max-w-md text-center">
                      <p className="text-[var(--nv-indigo)] font-semibold">
                        {selectedIdentityId ? "Ready when you are." : "Start by selecting an identity."}
                      </p>
                      <p className="text-sm text-[var(--nv-royal-purple)]/70 mt-2">
                        {selectedIdentityId
                          ? "Save your scene details, then hit Generate to create a first draft."
                          : "Once you pick an identity, you’ll be able to set the scene and generate an image draft here."}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Edit Image Section */}
            {generatedImageBase64 && selectedIdentity && (
              <div className="flex flex-col gap-4 border border-[var(--nv-royal-purple)]/20 rounded-lg p-4 bg-[var(--nv-pale-lavender)]/30">
                <h2 className="text-xl font-semibold text-[var(--nv-indigo)]">Refine</h2>
                <div className="space-y-2">
                  <label htmlFor="edit-prompt" className="text-sm font-medium text-[var(--nv-indigo)]">
                    Edit Instruction
                  </label>
                  <Textarea
                    id="edit-prompt"
                    placeholder="e.g., make the lighting warmer, change the background to a beach, add more vibrant colors..."
                    value={editPrompt}
                    onChange={(e) => setEditPrompt(e.target.value)}
                    rows={3}
                    className="w-full border-[var(--nv-royal-purple)]/30 focus:ring-[var(--nv-royal-purple)]"
                  />
                  <p className="text-xs text-[var(--nv-royal-purple)]/60">
                    Give one clear instruction at a time for best results.
                  </p>
                </div>

                <div className="flex flex-col gap-3">
                  <div className="flex items-center gap-3">
                    <Button
                      type="button"
                      variant="default"
                      onClick={handleEdit}
                      disabled={!canEdit}
                      className="h-10 px-6 bg-[var(--nv-royal-purple)] hover:bg-[var(--nv-royal-purple)]/90"
                    >
                      <Sparkles className="size-4" />
                      Apply Edit
                    </Button>
                    <div className="flex-1 min-w-0">
                      <GenerationStatus
                        isLoading={isContinuingChat}
                        error={editError}
                        onDismissError={handleDismissEditError}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Lightbox for current identity image */}
      {isCurrentIdentityImageOpen && selectedIdentity && currentIdentityFullUrl && (
        <div
          className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
          role="dialog"
          aria-modal="true"
          aria-label="Current identity image preview"
          onClick={() => setIsCurrentIdentityImageOpen(false)}
        >
          <div
            className="relative w-full max-w-5xl max-h-[90vh] bg-white/95 rounded-xl border border-white/20 shadow-lg overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              type="button"
              onClick={() => setIsCurrentIdentityImageOpen(false)}
              className="absolute top-3 right-3 inline-flex items-center justify-center rounded-md bg-black/10 hover:bg-black/20 transition-colors p-2"
              aria-label="Close image preview"
            >
              <X className="size-4 text-black/70" />
            </button>

            <div className="p-4 border-b border-black/10">
              <div className="flex items-center gap-2 flex-wrap">
                <div className="font-semibold text-[var(--nv-indigo)]">
                  {selectedIdentity.name}
                </div>
                {selectedIdentity.category &&
                  (() => {
                    const IconComponent = getIdentityCategoryIcon(
                      String(selectedIdentity.category)
                    );
                    const colorClasses = getIdentityCategoryColor(
                      String(selectedIdentity.category)
                    );
                    return (
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${colorClasses}`}
                      >
                        <IconComponent className="w-3 h-3" />
                        <span>
                          {getIdentityCategoryDisplayName(
                            String(selectedIdentity.category)
                          )}
                        </span>
                      </span>
                    );
                  })()}
              </div>
              <p className="text-xs text-black/50 mt-1">
                Press Escape or click outside to close.
              </p>
            </div>

            <div className="p-4 bg-[var(--nv-lilac-white)]">
              <div className="w-full h-[70vh] flex items-center justify-center">
                <img
                  src={currentIdentityFullUrl}
                  alt={`${selectedIdentity.name} current identity image`}
                  className="w-full h-full object-contain rounded-md"
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
