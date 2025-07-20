import { useQuery } from "@tanstack/react-query";
import { fetchTestScenarioUserIdentities } from "@/api/testScenarioUser";

/**
 * useTestScenarioUserIdentities
 * Fetches and caches identities for a test scenario user.
 */
export function useTestScenarioUserIdentities(userId: string) {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["testScenarioUser", userId, "identities"],
    queryFn: () => fetchTestScenarioUserIdentities(userId),
    enabled: !!userId,
    staleTime: 1000 * 60 * 10,
    retry: false,
  });
  return {
    identities: data,
    isLoading,
    isError,
    refetchIdentities: refetch,
  };
}