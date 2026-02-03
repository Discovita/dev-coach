/**
 * useImageGeneration hook
 * -----------------------
 * Handles identity image generation using TanStack Query mutations.
 * Provides functions for generating and saving identity images.
 *
 * Usage:
 *   const { generateImage, saveImage, isGenerating, isSaving } = useImageGeneration();
 */
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  generateIdentityImage,
  saveGeneratedImage,
  startImageChat,
  continueImageChat,
} from "@/api/imageGeneration";
import {
  GenerateImageRequest,
  GenerateImageResponse,
  SaveImageRequest,
  SaveImageResponse,
  StartImageChatRequest,
  StartImageChatResponse,
  ContinueImageChatRequest,
  ContinueImageChatResponse,
} from "@/types/imageGeneration";
import { toast } from "sonner";

/**
 * Hook for generating and saving identity images.
 * @returns Mutation functions for image generation and saving
 */
export function useImageGeneration() {
  const queryClient = useQueryClient();

  // Generate image mutation
  const generateMutation = useMutation<
    GenerateImageResponse,
    Error,
    GenerateImageRequest
  >({
    mutationFn: generateIdentityImage,
    onSuccess: () => {
      toast.success("Image generated successfully!");
    },
    onError: (error) => {
      toast.error(`Failed to generate image: ${error.message}`);
    },
  });

  // Save image mutation
  const saveMutation = useMutation<SaveImageResponse, Error, SaveImageRequest>(
    {
      mutationFn: saveGeneratedImage,
      onSuccess: () => {
        // Invalidate identities queries to refresh the identity with new image
        queryClient.invalidateQueries({ queryKey: ["user", "identities"] });
        queryClient.invalidateQueries({ queryKey: ["testScenarioUser"] });
        toast.success("Image saved to identity successfully!");
      },
      onError: (error) => {
        toast.error(`Failed to save image: ${error.message}`);
      },
    }
  );

  // Start chat mutation
  const startChatMutation = useMutation<
    StartImageChatResponse,
    Error,
    StartImageChatRequest
  >({
    mutationFn: startImageChat,
    onSuccess: () => {
      toast.success("Image generated successfully!");
    },
    onError: (error) => {
      toast.error(`Failed to generate image: ${error.message}`);
    },
  });

  // Continue chat mutation
  const continueChatMutation = useMutation<
    ContinueImageChatResponse,
    Error,
    ContinueImageChatRequest
  >({
    mutationFn: continueImageChat,
    onSuccess: () => {
      toast.success("Image edited successfully!");
    },
    onError: (error) => {
      toast.error(`Failed to edit image: ${error.message}`);
    },
  });

  return {
    // Legacy generate/save (kept for backwards compatibility)
    generateImage: generateMutation.mutateAsync,
    saveImage: saveMutation.mutateAsync,
    isGenerating: generateMutation.isPending,
    isSaving: saveMutation.isPending,
    generateError: generateMutation.error,
    saveError: saveMutation.error,
    generateData: generateMutation.data,
    saveData: saveMutation.data,
    resetGenerate: generateMutation.reset,
    resetSave: saveMutation.reset,
    // New chat-based mutations
    startChat: startChatMutation.mutateAsync,
    continueChat: continueChatMutation.mutateAsync,
    isStartingChat: startChatMutation.isPending,
    isContinuingChat: continueChatMutation.isPending,
    startChatError: startChatMutation.error,
    continueChatError: continueChatMutation.error,
    startChatData: startChatMutation.data,
    continueChatData: continueChatMutation.data,
    resetStartChat: startChatMutation.reset,
    resetContinueChat: continueChatMutation.reset,
  };
}

