/**
 * useReferenceImages hook
 * -----------------------
 * Fetches and manages reference images using TanStack Query.
 * Provides CRUD operations for reference images.
 *
 * Usage:
 *   const { data, isLoading, createImage, updateImage, deleteImage, uploadImage } = useReferenceImages(userId);
 *   // data is ReferenceImage[]
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listReferenceImages,
  createReferenceImage,
  updateReferenceImage,
  deleteReferenceImage,
  uploadReferenceImage,
} from "@/api/referenceImages";
import {
  ReferenceImage,
  CreateReferenceImageRequest,
  UpdateReferenceImageRequest,
} from "@/types/referenceImage";

/**
 * Hook for managing reference images for a specific user.
 * @param userId - Optional user ID (admin only). If not provided, uses current user.
 * @returns Query and mutation functions for reference images
 */
export function useReferenceImages(userId?: string) {
  const queryClient = useQueryClient();
  const queryKey = userId
    ? ["reference-images", userId]
    : ["reference-images", "current"];

  // Fetch reference images
  const {
    data,
    isLoading,
    isError,
    refetch,
  } = useQuery<ReferenceImage[]>({
    queryKey,
    queryFn: () => listReferenceImages(userId),
    staleTime: 1000 * 60 * 5, // 5 minutes cache
    retry: false,
  });

  // Create reference image mutation
  const createMutation = useMutation({
    mutationFn: async ({
      data: imageData,
      imageFile,
    }: {
      data: CreateReferenceImageRequest;
      imageFile?: File;
    }) => {
      return createReferenceImage(imageData, imageFile);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
    },
  });

  // Update reference image mutation
  const updateMutation = useMutation({
    mutationFn: async ({
      id,
      data: imageData,
    }: {
      id: string;
      data: UpdateReferenceImageRequest;
    }) => {
      return updateReferenceImage(id, imageData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
    },
  });

  // Delete reference image mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      return deleteReferenceImage(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
    },
  });

  // Upload image mutation
  const uploadMutation = useMutation({
    mutationFn: async ({
      id,
      imageFile,
    }: {
      id: string;
      imageFile: File;
    }) => {
      return uploadReferenceImage(id, imageFile);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
    },
  });

  return {
    referenceImages: data || [],
    isLoading,
    isError,
    refetch,
    createImage: createMutation.mutateAsync,
    updateImage: updateMutation.mutateAsync,
    deleteImage: deleteMutation.mutateAsync,
    uploadImage: uploadMutation.mutateAsync,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    isUploading: uploadMutation.isPending,
  };
}

