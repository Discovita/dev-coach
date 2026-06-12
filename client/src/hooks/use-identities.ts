import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchIdentities } from "@/api/user";
import { fetchTestScenarioUserIdentities } from "@/api/testScenarioUser";
import { reorderIdentities } from "@/api/identities";
import { useUserTarget } from "@/context/UserTargetContext";
import type { Identity } from "@/types/identity";

/**
 * useIdentities hook
 * Handles fetching the user's identities using TanStack Query.
 *
 * Context-aware: reads from UserTargetContext to determine query key prefix
 * and which API endpoint to call. When inside a UserTargetProvider, fetches
 * from the admin test-user endpoint instead of /user/me/.
 *
 * Also exposes a `reorder` mutation (logged-in user only) that optimistically
 * updates the cached order so drag-to-reorder feels instant, then persists via
 * POST /identities/reorder.
 *
 * Used in: Any component that needs to read the user's identities.
 */
export function useIdentities() {
	const { isImpersonating, targetUserId, queryKeyPrefix } = useUserTarget();
	const queryClient = useQueryClient();
	const identitiesKey = [...queryKeyPrefix, "identities"];

	const { data, isLoading, isError, refetch } = useQuery<Identity[]>({
		queryKey: identitiesKey,
		queryFn: isImpersonating
			? () => fetchTestScenarioUserIdentities(targetUserId!)
			: fetchIdentities,
		enabled: isImpersonating ? !!targetUserId : true,
		staleTime: 1000 * 60 * 10,
		retry: false,
	});

	const reorderMutation = useMutation<
		Identity[],
		Error,
		string[],
		{ previous: Identity[] | undefined }
	>({
		mutationFn: (orderedIds: string[]) => reorderIdentities(orderedIds),
		onMutate: async (orderedIds: string[]) => {
			// Optimistically apply the new order to the cache for an instant UI.
			await queryClient.cancelQueries({ queryKey: identitiesKey });
			const previous = queryClient.getQueryData<Identity[]>(identitiesKey);

			if (previous) {
				const byId = new Map(previous.map((i) => [i.id, i]));
				const reordered = orderedIds
					.map((id) => byId.get(id))
					.filter((i): i is Identity => Boolean(i));
				// Keep any identities not in orderedIds (e.g. filtered out) at the end.
				const remaining = previous.filter(
					(i) => !orderedIds.includes(i.id ?? ""),
				);
				queryClient.setQueryData<Identity[]>(identitiesKey, [
					...reordered,
					...remaining,
				]);
			}

			return { previous };
		},
		onError: (_err, _orderedIds, context) => {
			if (context?.previous) {
				queryClient.setQueryData(identitiesKey, context.previous);
			}
		},
		onSettled: () => {
			queryClient.invalidateQueries({ queryKey: identitiesKey });
		},
	});

	return {
		identities: data,
		isLoading,
		isError,
		refetchIdentities: refetch,
		reorderIdentities: reorderMutation.mutate,
		isReordering: reorderMutation.isPending,
	};
}
