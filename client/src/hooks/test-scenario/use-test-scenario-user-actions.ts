import { useQuery } from "@tanstack/react-query";
import { Action } from "@/types/action";

/**
 * useTestScenarioUserActions hook
 * Retrieves the running list of all actions for a test scenario user from the TanStack Query cache.
 * Updates reactively when new actions are added.
 * Used in: Any test scenario component that needs to display all actions received from the coach so far.
 */
export function useTestScenarioUserActions(userId: string): Action[] {
  // Use useQuery to subscribe to changes in the actions cache for the test user
  const { data } = useQuery<Action[]>({
    queryKey: ["testScenarioUser", userId, "actions"],
    // No fetcher: this is only set by mutation, so return empty array if not present
    queryFn: () => [],
  });
  return data || [];
} 