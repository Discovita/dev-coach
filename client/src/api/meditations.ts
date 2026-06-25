import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";

/**
 * Meditations API
 * ---------------
 * Public backend-driven feature flag for the Meditations feature.
 *
 * Endpoint: GET /api/v1/core/public/meditations
 * Permission: AllowAny
 */

export interface MeditationsConfig {
	enabled: boolean;
}

export async function fetchMeditationsConfig(): Promise<MeditationsConfig> {
	const response = await authFetch(`${COACH_BASE_URL}/core/public/meditations`);
	if (!response.ok) {
		throw new Error("Failed to fetch meditations config");
	}
	return response.json();
}
