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
  ImageGenerationError,
  ImageGenerationErrorCode,
} from "@/types/imageGeneration";
import { toast } from "sonner";

/**
 * Parsed error information for display in UI.
 */
export interface ParsedImageError {
  message: string;
  errorCode: ImageGenerationErrorCode;
  details: string | null;
  isRetryable: boolean;
}

/**
 * Parse an error into a structured format for UI display.
 */
export function parseImageError(error: Error | null): ParsedImageError | null {
  if (!error) return null;
  
  if (error instanceof ImageGenerationError) {
    // Determine if the error is retryable (user can try again without changes)
    const retryableCodes: ImageGenerationErrorCode[] = [
      "MODEL_OVERLOADED",
      "RATE_LIMITED",
      "EMPTY_RESPONSE",
    ];
    
    return {
      message: error.message,
      errorCode: error.error_code,
      details: error.details,
      isRetryable: retryableCodes.includes(error.error_code),
    };
  }
  
  // Generic error
  return {
    message: error.message || "An unexpected error occurred. Please try again.",
    errorCode: "UNKNOWN",
    details: null,
    isRetryable: true,
  };
}

/**
 * Get a user-friendly error message based on the error type.
 * Provides specific guidance for different error scenarios.
 */
function getErrorMessage(error: Error): string {
  if (error instanceof ImageGenerationError) {
    // The error message from the backend is already user-friendly
    return error.message;
  }
  // Fallback for generic errors
  return error.message || "An unexpected error occurred. Please try again.";
}

/**
 * Get the appropriate toast duration based on error type.
 * Longer duration for errors that need user action.
 */
function getToastDuration(error: Error): number {
  if (error instanceof ImageGenerationError) {
    // Give users more time to read actionable error messages
    return 8000;
  }
  return 5000;
}

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
      const message = getErrorMessage(error);
      toast.error(message, { duration: getToastDuration(error) });
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
      const message = getErrorMessage(error);
      toast.error(message, { duration: getToastDuration(error) });
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
      const message = getErrorMessage(error);
      toast.error(message, { duration: getToastDuration(error) });
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

