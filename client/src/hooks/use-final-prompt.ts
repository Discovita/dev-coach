import { useQuery } from "@tanstack/react-query";

/**
 * useFinalPrompt hook
 * Retrieves the latest final_prompt from the TanStack Query cache.
 * Updates reactively when the value changes.
 * Used in: Any component that needs to display the latest final prompt from the coach.
 */
export function useFinalPrompt(): string | undefined {
  // Use useQuery to subscribe to changes in the finalPrompt cache
  const { data } = useQuery<string | undefined>({
    queryKey: ["user", "finalPrompt"],
    // No fetcher: this is only set by mutation, so return undefined if not present
    queryFn: () => undefined,
  });
  return data;
}
