import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchActions } from "@/api/user";

/**
 * useActions hook
 * Handles fetching and updating the user's actions using TanStack Query.
 *
 * Step-by-step:
 * 1. Fetch the user's actions from /api/actions/ using getActions.
 * 2. Expose loading, error, and data states for UI consumption.
 * 3. Provide a mutation for updating actions (to be implemented as needed).
 * 4. Invalidate the query on successful update to keep data fresh.
 *
 * Used in: Any component that needs to read or update the user's actions.
 */
export function useActions() {
  const queryClient = useQueryClient();

  // Fetch the user's actions
  const {
    data,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["user", "actions"],
    queryFn: fetchActions,
  });

  // Placeholder for update mutation (implement as needed)
  // The argument will be added when the update API is implemented
  const updateMutation = useMutation({
    mutationFn: async () => {
      // Implement update API call here
      throw new Error("Update actions not implemented");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user", "actions"] });
    },
  });

  return {
    actions: data || [],
    isLoading,
    isError,
    refetchActions: refetch,
    updateActions: updateMutation.mutateAsync,
    updateStatus: updateMutation.status,
  };
}
