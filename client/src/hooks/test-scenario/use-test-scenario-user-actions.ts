import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchTestScenarioUserActions } from "@/api/testScenarioUser";

/**
 * useTestScenarioUserActions hook
 * Retrieves all actions for a specific test user from the database.
 * Used in: Test scenario visualizer components.
 * @param testUserId - The ID of the test user to get actions for
 */
export function useTestScenarioUserActions(testUserId: string) {
  const queryClient = useQueryClient();

  // Fetch the test user's actions
  const {
    data,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["test-scenario-user", testUserId, "actions"],
    queryFn: () => fetchTestScenarioUserActions(testUserId),
    enabled: !!testUserId,
  });

  // Placeholder for update mutation (implement as needed)
  // The argument will be added when the update API is implemented
  const updateMutation = useMutation({
    mutationFn: async () => {
      // Implement update API call here
      throw new Error("Update test scenario actions not implemented");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["test-scenario-user", testUserId, "actions"] });
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