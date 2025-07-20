import { useQuery } from "@tanstack/react-query";
import { fetchTestScenarioUserCoachState } from "@/api/testScenarioUser";

/**
 * useTestScenarioUserCoachState
 * Fetches and caches coach state for a test scenario user.
 * Returns the same shape as useCoachState for compatibility.
 */
export function useTestScenarioUserCoachState(userId: string) {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["testScenarioUser", userId, "coachState"],
    queryFn: () => fetchTestScenarioUserCoachState(userId),
    enabled: !!userId,
    staleTime: 1000 * 60 * 10,
    retry: false,
  });
  return {
    coachState: data,
    isLoading,
    isError,
    refetchCoachState: refetch,
  };
} 