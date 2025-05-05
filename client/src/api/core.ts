import { COACH_BASE_URL } from "@/constants/api";

/**
 * Fetch all enums for coach_states, allowed_actions, and context_keys.
 * Used for populating dropdowns/selects in the frontend prompt management UI.
 * Returns an object with arrays for each enum type.
 */
export async function fetchEnums() {
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
