import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchCoachState } from "@/api/user";

/**
 * useCoachState hook
 * Handles fetching and updating the user's coach state using TanStack Query.
 *
 * Step-by-step:
 * 1. Fetch the user's coach state from /user/me/coach-state/ using fetchCoachState.
 * 2. Expose loading, error, and data states for UI consumption.
 * 3. Provide a mutation for updating coach state (to be implemented as needed).
 * 4. Invalidate the query on successful update to keep data fresh.
 *
 * Used in: Any component that needs to read or update the user's coach state.
 */
export function useCoachState() {
  const queryClient = useQueryClient();

  // Fetch the user's coach state
  const {
    data,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["user", "coachState"],
    queryFn: fetchCoachState,
    staleTime: 0, // Reduced to 0 for more responsive updates
    retry: false,
  });

  // Placeholder for update mutation (implement as needed)
  // The argument will be added when the update API is implemented
  const updateMutation = useMutation({
    mutationFn: async () => {
      // Implement update API call here
      throw new Error("Update coach state not implemented");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user", "coachState"] });
    },
  });

  return {
    coachState: data,
    isLoading,
    isError,
    refetchCoachState: refetch,
    updateCoachState: updateMutation.mutateAsync,
    updateStatus: updateMutation.status,
  };
} 