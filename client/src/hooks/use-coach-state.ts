import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { fetchCoachState } from "@/api/user";
import { fetchTestScenarioUserCoachState } from "@/api/testScenarioUser";
import { useUserTarget } from "@/context/UserTargetContext";
import type { CoachState } from "@/types/coachState";

type UseCoachStateResult = {
  coachState: CoachState | undefined;
  isLoading: boolean;
  isError: boolean;
  refetchCoachState: UseQueryResult<CoachState, Error>["refetch"];
};

/**
 * useCoachState hook
 * Handles fetching the coach state using TanStack Query.
 *
 * Context-aware: reads from UserTargetContext to determine query key prefix
 * and which API endpoint to call. When inside a UserTargetProvider, fetches
 * from the admin test-user endpoint instead of /user/me/.
 *
 * Used in: Any component that needs to read the coach state.
 */
export function useCoachState(): UseCoachStateResult {
  const { isImpersonating, targetUserId, queryKeyPrefix } = useUserTarget();

  const { data, isLoading, isError, refetch } = useQuery<CoachState, Error>({
    queryKey: [...queryKeyPrefix, "coachState"],
    queryFn: isImpersonating
      ? () => fetchTestScenarioUserCoachState(targetUserId!)
      : fetchCoachState,
    enabled: isImpersonating ? !!targetUserId : true,
    staleTime: 0,
    retry: false,
  });

  return {
    coachState: data,
    isLoading,
    isError,
    refetchCoachState: refetch,
  };
}
