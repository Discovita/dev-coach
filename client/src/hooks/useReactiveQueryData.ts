import { useQueryClient } from "@tanstack/react-query";
import { useSyncExternalStore } from "react";

/**
 * useReactiveQueryData hook
 * Subscribes to TanStack Query's cache for a given query key and returns the current value.
 * Triggers a re-render whenever the cache for that key changes.
 *
 * @param queryKey - The query key to watch in the cache
 * @returns The cached data for the query key, or undefined if not present
 *
 * Usage:
 *   const profile = useReactiveQueryData<User>(["user", "profile"]);
 *   const isAdmin = useReactiveQueryData<boolean>(["user", "isAdmin"]);
 */
export function useReactiveQueryData<T>(queryKey: unknown[]): T | undefined {
  const queryClient = useQueryClient();
  return useSyncExternalStore(
    (cb) => queryClient.getQueryCache().subscribe(cb),
    () => queryClient.getQueryData<T>(queryKey)
  );
} 