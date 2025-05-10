import { useQuery } from "@tanstack/react-query";
import { Action } from "@/types/action";

/**
 * useActionsHistory hook
 * Retrieves the running list of all actions from the TanStack Query cache.
 * Updates reactively when new actions are added.
 * Used in: Any component that needs to display all actions received from the coach so far.
 */
export function useActions(): Action[] {
  // Use useQuery to subscribe to changes in the actions cache
  const { data } = useQuery<Action[]>({
    queryKey: ["user", "actions"],
    // No fetcher: this is only set by mutation, so return empty array if not present
    queryFn: () => [],
  });
  return data || [];
}
