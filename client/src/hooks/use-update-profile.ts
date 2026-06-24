import { updateUserProfile } from "@/api/user";
import type { User } from "@/types/user";
import { useMutation, useQueryClient } from "@tanstack/react-query";

/**
 * useUpdateProfile hook
 * ---------------------
 * Mutation for partially updating the current user's profile (e.g. first/last
 * name) via PATCH /user/me/. On success it writes the returned profile straight
 * into the ["user", "profile"] cache so the UI reflects the change immediately.
 *
 * Used in: Account page name editing, onboarding name capture step.
 */
export function useUpdateProfile() {
	const queryClient = useQueryClient();

	const mutation = useMutation<
		User,
		Error,
		Partial<Pick<User, "first_name" | "last_name">>
	>({
		mutationFn: updateUserProfile,
		onSuccess: (data) => {
			queryClient.setQueryData(["user", "profile"], data);
			queryClient.invalidateQueries({ queryKey: ["user", "profile"] });
		},
	});

	return {
		updateProfile: mutation.mutateAsync,
		isUpdating: mutation.isPending,
		updateError: mutation.error,
	};
}
