import { fetchMeditationsConfig } from "@/api/meditations";
import { useQuery } from "@tanstack/react-query";

/**
 * useMeditations hook
 *
 * Backend-driven feature flag for the Meditations feature. The frontend asks
 * the backend whether the meditations surface should be shown, so the flag is
 * flipped in one place (a single env var on the backend).
 *
 * Fails CLOSED: `enabled` is false while loading or on error, so the surface
 * stays hidden unless the backend explicitly says it's on.
 */
export function useMeditations() {
	const query = useQuery({
		queryKey: ["meditations", "config"],
		queryFn: fetchMeditationsConfig,
		staleTime: 1000 * 60 * 5,
		retry: false,
	});

	return {
		...query,
		enabled: query.data?.enabled ?? false,
	};
}
