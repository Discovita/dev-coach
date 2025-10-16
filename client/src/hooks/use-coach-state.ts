import { useQuery } from "@tanstack/react-query";
import { fetchCoachState } from "@/api/user";

/**
 * useCoachState hook
 * Handles fetching and updating the user's coach state using TanStack Query.
 *
 * Step-by-step:
 * 1. Fetch the user's coach state from /user/me/coach-state/ using fetchCoachState.
 * 2. Expose loading, error, and data states for UI consumption.
 * 3. Provide a mutation for updating coach state (to be implemented as needed).
 * 4. Invalidate the query on successful update to keep data fresh.
 *
 * Used in: Any component that needs to read or update the user's coach state.
 */
export function useCoachState() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["user", "coachState"],
    queryFn: fetchCoachState,
    staleTime: 0, // Reduced to 0 for more responsive updates
    retry: false,
  });

  return {
    coachState: data,
    isLoading,
    isError,
    refetchCoachState: refetch,
  };
}
