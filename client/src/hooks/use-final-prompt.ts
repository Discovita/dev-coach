import { useQuery } from "@tanstack/react-query";
import { useUserTarget } from "@/context/UserTargetContext";

/**
 * useFinalPrompt hook
 * Retrieves the latest final_prompt from the TanStack Query cache.
 * Updates reactively when the value changes.
 *
 * This is a cache-only query — data is written by useChatMessages onSuccess,
 * not fetched from an API. The query is disabled to prevent refetches from
 * overwriting cached values.
 *
 * Context-aware: reads from UserTargetContext to determine query key prefix.
 * When inside a UserTargetProvider, uses scoped keys for the impersonated user.
 *
 * Used in: Any component that needs to display the latest final prompt from the coach.
 */
export function useFinalPrompt(): string | undefined {
  const { queryKeyPrefix } = useUserTarget();

  const { data } = useQuery<string | undefined>({
    queryKey: [...queryKeyPrefix, "finalPrompt"],
    queryFn: () => undefined,
    enabled: false,
  });
  return data;
}
