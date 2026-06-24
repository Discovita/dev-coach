import { COACH_BASE_URL } from "@/constants/api";
import { LogLevel, createLogger } from "@/lib/logger";
import type { UserAppearance } from "@/types/userAppearance";
import { authFetch } from "@/utils/authFetch";

const log = createLogger("userAppearanceApi", LogLevel.DEBUG);

/**
 * User Appearance API
 * -------------------
 * Functions for fetching and updating user appearance preferences.
 * These settings are stored on the User model and apply to all identity image generations.
 *
 * Endpoints covered:
 * - getUserAppearance:         GET   /api/v1/user/me/ (current user)
 * - updateUserAppearance:      PATCH /api/v1/user/me/ (current user)
 * - getTestUserAppearance:     GET   /api/v1/admin/test-user/{id}/profile (admin)
 * - updateTestUserAppearance:  PATCH /api/v1/admin/test-user/{id}/update-profile (admin)
 */

function extractAppearance(data: Record<string, unknown>): UserAppearance {
	return {
		gender: (data.gender as UserAppearance["gender"]) || null,
		skin_tone: (data.skin_tone as UserAppearance["skin_tone"]) || null,
		hair_color: (data.hair_color as UserAppearance["hair_color"]) || null,
		eye_color: (data.eye_color as UserAppearance["eye_color"]) || null,
		height: (data.height as UserAppearance["height"]) || null,
		build: (data.build as UserAppearance["build"]) || null,
		age_range: (data.age_range as UserAppearance["age_range"]) || null,
	};
}

/**
 * Get appearance preferences for the current authenticated user.
 * GET /api/v1/user/me/
 * @returns UserAppearance from user profile
 */
export async function getUserAppearance(): Promise<UserAppearance> {
	log.debug("Fetching user appearance");
	const response = await authFetch(`${COACH_BASE_URL}/user/me`, {});
	if (!response.ok) throw new Error("Failed to fetch user appearance");
	const data = await response.json();
	log.debug("Successfully fetched user appearance", data);
	return extractAppearance(data);
}

/**
 * Update appearance preferences for the current authenticated user.
 * PATCH /api/v1/user/me/
 * @param appearance - Partial UserAppearance to update
 * @returns Updated UserAppearance
 */
export async function updateUserAppearance(
	appearance: Partial<UserAppearance>,
): Promise<UserAppearance> {
	log.debug("Updating user appearance", appearance);
	const response = await authFetch(`${COACH_BASE_URL}/user/me`, {
		method: "PATCH",
		body: JSON.stringify(appearance),
	});
	if (!response.ok) {
		const error = await response
			.json()
			.catch(() => ({ error: "Failed to update user appearance" }));
		throw new Error(error.error || "Failed to update user appearance");
	}
	const data = await response.json();
	log.debug("Successfully updated user appearance", data);
	return extractAppearance(data);
}

/**
 * Get appearance preferences for a test scenario user (admin only).
 * GET /api/v1/admin/test-user/{id}/profile
 * @param userId - UUID of the user
 * @returns UserAppearance from user profile
 */
export async function getTestUserAppearance(
	userId: string,
): Promise<UserAppearance> {
	log.debug(`Fetching test user appearance for ${userId}`);
	const response = await authFetch(
		`${COACH_BASE_URL}/admin/test-user/${userId}/profile`,
		{},
	);
	if (!response.ok) throw new Error("Failed to fetch test user appearance");
	const data = await response.json();
	log.debug("Successfully fetched test user appearance", data);
	return extractAppearance(data);
}

/**
 * Update appearance preferences for a test scenario user (admin only).
 * PATCH /api/v1/admin/test-user/{id}/update-profile
 * @param userId - UUID of the user
 * @param appearance - Partial UserAppearance to update
 * @returns Updated UserAppearance
 */
export async function updateTestUserAppearance(
	userId: string,
	appearance: Partial<UserAppearance>,
): Promise<UserAppearance> {
	log.debug(`Updating test user appearance for ${userId}`, appearance);
	const response = await authFetch(
		`${COACH_BASE_URL}/admin/test-user/${userId}/update-profile`,
		{
			method: "PATCH",
			body: JSON.stringify(appearance),
		},
	);
	if (!response.ok) {
		const error = await response
			.json()
			.catch(() => ({ error: "Failed to update test user appearance" }));
		throw new Error(error.error || "Failed to update test user appearance");
	}
	const data = await response.json();
	log.debug("Successfully updated test user appearance", data);
	return extractAppearance(data);
}
