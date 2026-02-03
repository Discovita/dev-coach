import { useQuery } from "@tanstack/react-query";
import { fetchEnums } from "@/api/core";
import { CoreEnumsResponse } from "@/types/coreEnums";

/**
 * useCoreEnums hook
 * Fetches and caches all enums for coaching_phases, allowed_actions, context_keys, prompt_types, and appearance options.
 * - Uses TanStack Query for caching and reactivity.
 * - Returns data, loading, and error states.
 *
 * Usage:
 *   const { data, isLoading, isError, refetch } = useCoreEnums();
 *   // data?.coaching_phases, data?.allowed_actions, data?.context_keys, data?.prompt_types
 *   // data?.appearance.genders, data?.appearance.skin_tones, etc.
 */
export function useCoreEnums() {
  return useQuery<CoreEnumsResponse>({
    queryKey: ["core", "enums"],
    queryFn: fetchEnums,
    staleTime: 1000 * 60 * 60, // 1 hour cache by default
    retry: false,
  });
}
