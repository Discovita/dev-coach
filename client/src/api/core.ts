import { COACH_BASE_URL } from "@/constants/api";
import type { CoreEnumsResponse } from "@/types/coreEnums";
import { authFetch } from "@/utils/authFetch";

/**
 * Fetch all enums for coaching_phases, allowed_actions, context_keys, prompt_types, and appearance options.
 * Used for populating dropdowns/selects in the frontend prompt management UI.
 * Returns an object with arrays for each enum type.
 */
export async function fetchEnums(): Promise<CoreEnumsResponse> {
	const url = `${COACH_BASE_URL}/core/enums`;
	const response = await authFetch(url);
	if (!response.ok) {
		throw new Error("Failed to fetch core enums");
	}
	return response.json();
}
