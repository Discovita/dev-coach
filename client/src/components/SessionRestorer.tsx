import { getCookie } from "@/api/auth";
import { fetchUserComplete } from "@/api/user";
import type { User } from "@/types/user";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";

export function SessionRestorer() {
	const queryClient = useQueryClient();

	useEffect(() => {
		const profile = queryClient.getQueryData<User>(["user", "profile"]);
		if (!profile) {
			const accessToken = getCookie("discovita-access-token");
			if (accessToken) {
				fetchUserComplete().then((user) => {
					if (user) {
						queryClient.setQueryData(["user", "profile"], {
							id: user.id,
							email: user.email,
							first_name: user.first_name,
							last_name: user.last_name,
							is_active: user.is_active,
							is_superuser: user.is_superuser,
							is_staff: user.is_staff,
							last_login: user.last_login,
							created_at: user.created_at,
							updated_at: user.updated_at,
							groups: user.groups,
							user_permissions: user.user_permissions,
						});
						queryClient.setQueryData(["user", "coachState"], user.coach_state);
						queryClient.setQueryData(["user", "identities"], user.identities);
						queryClient.setQueryData(
							["user", "chatMessages"],
							user.chat_messages,
						);
						queryClient.setQueryData(["user", "complete"], user);
						queryClient.setQueryData(["user", "isAdmin"], !!user.is_staff);
					}
				});
			}
		}
	}, [queryClient]);

	return null;
}
