import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchIdentities } from "@/api/user";
import { fetchTestScenarioUserIdentities } from "@/api/testScenarioUser";
import { useUserTarget } from "@/context/UserTargetContext";

/**
 * useIdentities hook
 * Handles fetching the user's identities using TanStack Query.
 *
 * Context-aware: reads from UserTargetContext to determine query key prefix
 * and which API endpoint to call. When inside a UserTargetProvider, fetches
 * from the admin test-user endpoint instead of /user/me/.
 *
 * Used in: Any component that needs to read the user's identities.
 */
export function useIdentities() {
  const { isImpersonating, targetUserId, queryKeyPrefix } = useUserTarget();
  const queryClient = useQueryClient();

  const {
    data,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: [...queryKeyPrefix, "identities"],
    queryFn: isImpersonating
      ? () => fetchTestScenarioUserIdentities(targetUserId!)
      : fetchIdentities,
    enabled: isImpersonating ? !!targetUserId : true,
    staleTime: 1000 * 60 * 10,
    retry: false,
  });

  const updateMutation = useMutation({
    mutationFn: async () => {
      throw new Error("Update identities not implemented");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [...queryKeyPrefix, "identities"] });
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