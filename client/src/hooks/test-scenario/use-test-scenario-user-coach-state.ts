import { useQuery } from "@tanstack/react-query";
import { fetchTestScenarioUserCoachState } from "@/api/testScenarioUser";

/**
 * useTestScenarioUserCoachState
 * Fetches and caches coach state for a test scenario user.
 */
export function useTestScenarioUserCoachState(userId: string) {
  return useQuery({
    queryKey: ["testScenarioUser", userId, "coachState"],
    queryFn: () => fetchTestScenarioUserCoachState(userId),
    enabled: !!userId,
    staleTime: 1000 * 60 * 10,
    retry: false,
  });
} 