import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchActions } from "@/api/user";
import { fetchTestScenarioUserActions } from "@/api/testScenarioUser";
import { useUserTarget } from "@/context/UserTargetContext";

/**
 * useActions hook
 * Handles fetching the user's actions using TanStack Query.
 *
 * Context-aware: reads from UserTargetContext to determine query key prefix
 * and which API endpoint to call. When inside a UserTargetProvider, fetches
 * from the admin test-user endpoint instead of /user/me/.
 *
 * Used in: Any component that needs to read the user's actions.
 */
export function useActions() {
  const { isImpersonating, targetUserId, queryKeyPrefix } = useUserTarget();
  const queryClient = useQueryClient();

  const {
    data,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: [...queryKeyPrefix, "actions"],
    queryFn: isImpersonating
      ? () => fetchTestScenarioUserActions(targetUserId!)
      : fetchActions,
    enabled: isImpersonating ? !!targetUserId : true,
    staleTime: 1000 * 60 * 10,
    retry: false,
  });

  const updateMutation = useMutation({
    mutationFn: async () => {
      throw new Error("Update actions not implemented");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [...queryKeyPrefix, "actions"] });
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
