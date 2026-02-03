import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getUserAppearance,
  updateUserAppearance,
  getTestUserAppearance,
  updateTestUserAppearance,
} from "@/api/userAppearance";
import { UserAppearance } from "@/types/userAppearance";
import { useProfile } from "./use-profile";

/**
 * useUserAppearance hook
 * ----------------------
 * Handles fetching and updating user appearance preferences using TanStack Query.
 *
 * Step-by-step:
 * 1. Determines if the userId is the current user or a test user
 * 2. Fetches appearance data from appropriate endpoint
 * 3. Provides mutation for updating appearance
 * 4. Invalidates queries on successful update to keep data fresh
 *
 * Used in: Images page for appearance customization
 */
export function useUserAppearance(userId: string | null) {
  const queryClient = useQueryClient();
  const { profile } = useProfile();
  const isCurrentUser = profile && userId === profile.id;

  // Fetch appearance data
  const {
    data,
    isLoading,
    isError,
    refetch,
  } = useQuery<UserAppearance | null, Error>({
    queryKey: ["user", userId, "appearance"],
    queryFn: async () => {
      if (!userId) return null;
      if (isCurrentUser) {
        return getUserAppearance();
      } else {
        return getTestUserAppearance(userId);
      }
    },
    enabled: !!userId,
    staleTime: 1000 * 60 * 10, // 10 minutes
    retry: false,
  });

  // Update appearance mutation
  const updateMutation = useMutation<UserAppearance, Error, Partial<UserAppearance>>({
    mutationFn: async (appearance: Partial<UserAppearance>) => {
      if (!userId) throw new Error("User ID is required");
      if (isCurrentUser) {
        return updateUserAppearance(appearance);
      } else {
        return updateTestUserAppearance(userId, appearance);
      }
    },
    onSuccess: () => {
      // Invalidate appearance query
      queryClient.invalidateQueries({ queryKey: ["user", userId, "appearance"] });
      // Also invalidate user profile queries to keep them in sync
      if (isCurrentUser) {
        queryClient.invalidateQueries({ queryKey: ["user", "profile"] });
      } else {
        queryClient.invalidateQueries({ queryKey: ["testScenarioUser", userId] });
      }
    },
  });

  return {
    appearance: data || null,
    isLoading,
    isError,
    refetchAppearance: refetch,
    updateAppearance: updateMutation.mutateAsync,
    isUpdating: updateMutation.isPending,
    updateError: updateMutation.error,
  };
}
