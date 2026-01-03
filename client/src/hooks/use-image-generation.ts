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
} from "@/api/imageGeneration";
import {
  GenerateImageRequest,
  GenerateImageResponse,
  SaveImageRequest,
  SaveImageResponse,
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

  return {
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
  };
}

