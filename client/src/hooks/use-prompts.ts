/**
 * usePrompts hook
 * --------------
 * Fetches and caches all prompts from the backend.
 * Uses TanStack Query for caching and reactivity.
 * Returns data, loading, and error states.
 *
 * Usage:
 *   const { data, isLoading, isError, refetch } = usePrompts();
 *   // data is Prompt[]
 */
import { useQuery } from "@tanstack/react-query";
import { fetchAllPrompts } from "@/api/prompts";
import { Prompt } from "@/types/prompt";

export function usePrompts() {
  return useQuery<Prompt[]>({
    queryKey: ["prompts", "all"],
    queryFn: fetchAllPrompts,
    staleTime: 1000 * 60 * 10, // 10 minutes cache by default
    retry: false,
  });
}
