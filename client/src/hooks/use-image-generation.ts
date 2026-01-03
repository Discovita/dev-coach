/**
 * useImageGeneration hook
 * -----------------------
 * Handles identity image generation using TanStack Query mutations.
 * Provides functions for generating and saving identity images.
 *
 * Usage:
 *   const { generateImage, saveImage, isGenerating, isSaving } = useImageGeneration();
 */
import { useMutation } from "@tanstack/react-query";
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

/**
 * Hook for generating and saving identity images.
 * @returns Mutation functions for image generation and saving
 */
export function useImageGeneration() {
  // Generate image mutation
  const generateMutation = useMutation<
    GenerateImageResponse,
    Error,
    GenerateImageRequest
  >({
    mutationFn: generateIdentityImage,
  });

  // Save image mutation
  const saveMutation = useMutation<SaveImageResponse, Error, SaveImageRequest>(
    {
      mutationFn: saveGeneratedImage,
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

