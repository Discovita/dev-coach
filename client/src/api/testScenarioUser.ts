import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";

/**
 * Test Scenario User API
 * ----------------------
 * Admin-only functions for fetching data belonging to test scenario users.
 * These mirror the regular user endpoints but operate on a specific user
 * identified by userId, via the /admin/test-user/{userId}/ prefix.
 *
 * Ported from: dev-coach/client/src/api/testScenarioUser.ts
 */

/**
 * Fetch profile data for a test scenario user (admin only).
 * GET /api/v1/admin/test-user/{userId}/profile/
 */
export async function fetchTestScenarioUserProfile(userId: string) {
	const response = await authFetch(
		`${COACH_BASE_URL}/admin/test-user/${userId}/profile`,
		{},
	);
	if (!response.ok)
		throw new Error("Failed to fetch test scenario user profile");
	return response.json();
}

/**
 * Fetch complete user data for a test scenario user (admin only).
 * GET /api/v1/admin/test-user/{userId}/complete/
 */
export async function fetchTestScenarioUserComplete(userId: string) {
	const response = await authFetch(
		`${COACH_BASE_URL}/admin/test-user/${userId}/complete`,
		{},
	);
	if (!response.ok) throw new Error("Failed to fetch test scenario user data");
	return response.json();
}

/**
 * Fetch coach state for a test scenario user (admin only).
 * GET /api/v1/admin/test-user/{userId}/coach-state/
 */
export async function fetchTestScenarioUserCoachState(userId: string) {
	const response = await authFetch(
		`${COACH_BASE_URL}/admin/test-user/${userId}/coach-state`,
		{},
	);
	if (!response.ok)
		throw new Error("Failed to fetch test scenario user coach state");
	return response.json();
}

/**
 * Set the tri-state Studio access override for a user (super-admin only).
 * PATCH /api/v1/admin/test-user/{userId}/studio-access
 *
 * `override`: `true` forces the Studio unlocked, `false` forces it locked,
 * `null` restores the default phase-based unlock. Returns the updated
 * coach-state payload.
 */
export async function setStudioAccessOverride(
	userId: string,
	override: boolean | null,
) {
	const response = await authFetch(
		`${COACH_BASE_URL}/admin/test-user/${userId}/studio-access`,
		{
			method: "PATCH",
			body: JSON.stringify({ studio_access_override: override }),
		},
	);
	if (!response.ok) throw new Error("Failed to update Studio access");
	return response.json();
}

/**
 * Fetch identities for a test scenario user (admin only).
 * GET /api/v1/admin/test-user/{userId}/identities/
 */
export async function fetchTestScenarioUserIdentities(userId: string) {
	const response = await authFetch(
		`${COACH_BASE_URL}/admin/test-user/${userId}/identities`,
		{},
	);
	if (!response.ok)
		throw new Error("Failed to fetch test scenario user identities");
	return response.json();
}

/**
 * Fetch actions for a test scenario user (admin only).
 * GET /api/v1/admin/test-user/{userId}/actions/
 */
export async function fetchTestScenarioUserActions(userId: string) {
	const response = await authFetch(
		`${COACH_BASE_URL}/admin/test-user/${userId}/actions`,
		{},
	);
	if (!response.ok)
		throw new Error("Failed to fetch test scenario user actions");
	return response.json();
}

/**
 * Fetch chat messages for a test scenario user (admin only).
 * GET /api/v1/admin/test-user/{userId}/chat-messages/
 */
export async function fetchTestScenarioChatMessages(userId: string) {
	const response = await authFetch(
		`${COACH_BASE_URL}/admin/test-user/${userId}/chat-messages`,
		{},
	);
	if (!response.ok)
		throw new Error("Failed to fetch test scenario user chat messages");
	return response.json();
}
