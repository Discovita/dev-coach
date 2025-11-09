import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { fetchTestScenarioUserCoachState } from "@/api/testScenarioUser";
import type { CoachState } from "@/types/coachState";

type UseTestScenarioUserCoachStateResult = {
  coachState: CoachState | undefined;
  isLoading: boolean;
  isError: boolean;
  refetchCoachState: UseQueryResult<CoachState, Error>["refetch"];
};

/**
 * useTestScenarioUserCoachState
 * Fetches and caches coach state for a test scenario user.
 * Returns the same shape as useCoachState for compatibility.
 */
export function useTestScenarioUserCoachState(userId: string): UseTestScenarioUserCoachStateResult {
  const { data, isLoading, isError, refetch } = useQuery<CoachState, Error>({
    queryKey: ["testScenarioUser", userId, "coachState"],
    queryFn: () => fetchTestScenarioUserCoachState(userId),
    enabled: !!userId,
    staleTime: 0, // Reduced from 10 minutes to 0 for more responsive updates
    retry: false,
  });
  return {
    coachState: data,
    isLoading,
    isError,
    refetchCoachState: refetch,
  };
} 