import { useQuery } from "@tanstack/react-query";
import { fetchTestScenarioUserComplete } from "@/api/testScenarioUser";

/**
 * useTestScenarioUser
 * Fetches and caches complete user data for a test scenario user.
 * Used only for test scenario chat windows.
 */
export function useTestScenarioUser(userId: string) {
  return useQuery({
    queryKey: ["testScenarioUser", userId, "complete"],
    queryFn: () => fetchTestScenarioUserComplete(userId),
    enabled: !!userId, // Only run if userId is provided
    staleTime: 1000 * 60 * 10, // 10 minutes
    retry: false,
  });
} 