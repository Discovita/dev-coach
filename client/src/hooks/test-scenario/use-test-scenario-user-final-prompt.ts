import { useQuery } from "@tanstack/react-query";

/**
 * useTestScenarioUserFinalPrompt hook
 * Retrieves the latest final_prompt for a test scenario user from the TanStack Query cache.
 * Updates reactively when the value changes.
 * Used in: Any test scenario component that needs to display the latest final prompt from the coach.
 */
export function useTestScenarioUserFinalPrompt(userId: string): string | undefined {
  // Use useQuery to subscribe to changes in the finalPrompt cache for the test user
  const { data } = useQuery<string | undefined>({
    queryKey: ["testScenarioUser", userId, "finalPrompt"],
    // TanStack Query does not allow undefined as a return value from queryFn.
    // Return an empty string if not present to avoid errors.
    queryFn: () => "",
  });
  return data;
} 