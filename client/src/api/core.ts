import { COACH_BASE_URL } from "@/constants/api";
import { CoreEnumsResponse } from "@/types/coreEnums";

/**
 * Fetch all enums for coaching_phases, allowed_actions, context_keys, prompt_types, and appearance options.
 * Used for populating dropdowns/selects in the frontend prompt management UI.
 * Returns an object with arrays for each enum type.
 */
export async function fetchEnums(): Promise<CoreEnumsResponse> {
  const url = `${COACH_BASE_URL}/core/enums`;
  const response = await fetch(url, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  if (!response.ok) {
    throw new Error("Failed to fetch core enums");
  }
  return response.json();
}
