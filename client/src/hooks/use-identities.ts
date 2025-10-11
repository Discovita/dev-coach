import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchIdentities } from "@/api/user";

/**
 * useIdentities hook
 * Handles fetching and updating the user's identities using TanStack Query.
 *
 * Step-by-step:
 * 1. Fetch the user's identities from /user/me/identities/ using fetchIdentities.
 * 2. Expose loading, error, and data states for UI consumption.
 * 3. Provide a mutation for updating identities (to be implemented as needed).
 * 4. Invalidate the query on successful update to keep data fresh.
 *
 * Used in: Any component that needs to read or update the user's identities.
 */
export function useIdentities() {
  const queryClient = useQueryClient();

  // Fetch the user's identities
  const {
    data,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["user", "identities"],
    queryFn: fetchIdentities,
    staleTime: 1000 * 60 * 10, // 10 minutes
    retry: false,
  });

  // Placeholder for update mutation (implement as needed)
  // The argument will be added when the update API is implemented
  const updateMutation = useMutation({
    mutationFn: async () => {
      // Implement update API call here
      throw new Error("Update identities not implemented");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user", "identities"] });
    },
  });

  return {
    identities: data,
    isLoading,
    isError,
    refetchIdentities: refetch,
    updateIdentities: updateMutation.mutateAsync,
    updateStatus: updateMutation.status,
  };
} 