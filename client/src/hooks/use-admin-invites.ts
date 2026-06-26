import {
	type Invite,
	createInvite,
	fetchInvites,
	resendInvite,
	revokeInvite,
} from "@/api/adminInvites";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

/**
 * useAdminInvites hook
 *
 * Lists invites and exposes create / resend / revoke mutations for the
 * super-admin Invites panel. Backend enforces IsSuperUser.
 */
export function useAdminInvites() {
	const queryClient = useQueryClient();
	const invalidate = () =>
		queryClient.invalidateQueries({ queryKey: ["admin", "invites"] });

	const invitesQuery = useQuery<Invite[]>({
		queryKey: ["admin", "invites"],
		queryFn: fetchInvites,
		staleTime: 1000 * 60,
		retry: false,
	});

	const createMutation = useMutation({
		mutationFn: createInvite,
		onSuccess: invalidate,
	});

	const resendMutation = useMutation({
		mutationFn: resendInvite,
		onSuccess: invalidate,
	});

	const revokeMutation = useMutation({
		mutationFn: revokeInvite,
		onSuccess: invalidate,
	});

	return {
		invites: invitesQuery.data ?? [],
		isLoading: invitesQuery.isLoading,
		isError: invitesQuery.isError,
		createInvite: createMutation.mutateAsync,
		createStatus: createMutation.status,
		createError: createMutation.error as Error | null,
		resendInvite: resendMutation.mutateAsync,
		resendingId: resendMutation.isPending
			? resendMutation.variables
			: undefined,
		revokeInvite: revokeMutation.mutateAsync,
		revokingId: revokeMutation.isPending ? revokeMutation.variables : undefined,
	};
}
