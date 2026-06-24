import { COACH_BASE_URL, FREEZE_SESSION } from "@/constants/api";
import type { TestScenario } from "@/types/testScenario";
import { authFetch } from "@/utils/authFetch";
import { useMutation, useQueryClient } from "@tanstack/react-query";

/**
 * useFreezeTestScenarioSession
 * Hook to freeze a user's current session as a new test scenario.
 *
 * @returns { mutateAsync, isPending, error, data }
 * Usage: mutateAsync({ user_id, name, description, first_name?, last_name? })
 */
export function useFreezeTestScenarioSession() {
	const queryClient = useQueryClient();
	const mutation = useMutation({
		mutationFn: async (params: {
			user_id: string;
			name: string;
			description: string;
			first_name?: string;
			last_name?: string;
		}) => {
			const res = await authFetch(`${COACH_BASE_URL}${FREEZE_SESSION}`, {
				method: "POST",
				body: JSON.stringify(params),
				headers: { "Content-Type": "application/json" },
			});
			if (!res.ok) {
				const error = await res.json();
				throw error;
			}
			return (await res.json()) as TestScenario;
		},
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["test-scenarios", "all"] });
		},
	});
	return mutation;
}
