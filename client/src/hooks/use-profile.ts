import { fetchUserProfile } from "@/api/user";
import { isAdminUser } from "@/permissions/isAdminUser";
import type { User } from "@/types/user";
import { type UseQueryResult, useQuery } from "@tanstack/react-query";

type UseProfileResult = {
	profile: User | undefined;
	isAdmin: boolean | undefined;
	isLoading: boolean;
	isError: boolean;
	refetchProfile: UseQueryResult<User, Error>["refetch"];
};

/**
 * useProfile hook
 * Handles fetching and updating the user's profile using TanStack Query.
 *
 * Step-by-step:
 * 1. Fetch the user's profile from /user/me/ using fetchUserProfile.
 * 2. Expose loading, error, and data states for UI consumption.
 * 3. Create an active query subscription so profile updates automatically when invalidated.
 * 4. Note: Profile may be set directly in cache by useAuth or SessionRestorer after login.
 *    This hook will use that cached data if available and fresh, or fetch if needed.
 *
 * Used in: Any component that needs to read the user's profile.
 */
export function useProfile(): UseProfileResult {
	const { data, isLoading, isError, refetch } = useQuery<User, Error>({
		queryKey: ["user", "profile"],
		queryFn: fetchUserProfile,
		staleTime: 1000 * 60 * 10, // 10 minutes
		retry: false,
	});

	const isAdmin = data ? isAdminUser(data) : undefined;

	return {
		profile: data,
		isAdmin,
		isLoading,
		isError,
		refetchProfile: refetch,
	};
}
