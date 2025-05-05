import { useQuery } from "@tanstack/react-query";
import { fetchEnums } from "@/api/core";

/**
 * useCoreEnums hook
 * Fetches and caches all enums for coach_states, allowed_actions, and context_keys.
 * - Uses TanStack Query for caching and reactivity.
 * - Returns data, loading, and error states.
 *
 * Usage:
 *   const { data, isLoading, isError, refetch } = useCoreEnums();
 *   // data?.coach_states, data?.allowed_actions, data?.context_keys
 */
export function useCoreEnums() {
  return useQuery({
    queryKey: ["core", "enums"],
    queryFn: fetchEnums,
    staleTime: 1000 * 60 * 60, // 1 hour cache by default
    retry: false,
  });
}
