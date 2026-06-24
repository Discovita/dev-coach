import { COACH_BASE_URL } from "@/constants/api";
import { LogLevel, createLogger } from "@/lib/logger";
import type { User } from "@/types/user";
import { authFetch } from "@/utils/authFetch";

const log = createLogger("userApi", LogLevel.DEBUG);

/**
 * Fetch the current authenticated user's profile (basic info only).
 * Calls /user/me/
 */
export async function fetchUserProfile() {
	log.debug("Fetching user profile from /user/me");
	const response = await authFetch(`${COACH_BASE_URL}/user/me`, {});
	if (!response.ok) throw new Error("Failed to fetch user profile");
	const data = await response.json();
	log.debug("Successfully fetched user profile", data);
	return data;
}

/**
 * Update the current authenticated user's profile (partial).
 * PATCH /user/me/
 *
 * Used for editable profile fields such as first/last name.
 */
export async function updateUserProfile(
	updates: Partial<Pick<User, "first_name" | "last_name">>,
): Promise<User> {
	log.debug("Updating user profile", updates);
	const response = await authFetch(`${COACH_BASE_URL}/user/me`, {
		method: "PATCH",
		body: JSON.stringify(updates),
	});
	if (!response.ok) throw new Error("Failed to update profile");
	const data = await response.json();
	log.debug("Successfully updated user profile", data);
	return data;
}

/**
 * Fetch the current authenticated user's complete info (all nested data).
 * Calls /user/me/complete/
 */
export async function fetchUserComplete() {
	log.debug("Fetching complete user info from /user/me/complete");
	const response = await authFetch(`${COACH_BASE_URL}/user/me/complete`, {});
	if (!response.ok) throw new Error("Failed to fetch complete user info");
	const data = await response.json();
	log.debug("Successfully fetched complete user info", data);
	return data;
}

/**
 * Fetch the current authenticated user's coach state.
 * Calls /user/me/coach-state/
 */
export async function fetchCoachState() {
	log.debug("Fetching coach state from /user/me/coach-state");
	const response = await authFetch(`${COACH_BASE_URL}/user/me/coach-state`, {});
	if (!response.ok) throw new Error("Failed to fetch coach state");
	const data = await response.json();
	log.debug("Successfully fetched coach state", data);
	return data;
}

/**
 * Fetch the current authenticated user's identities.
 * Calls /user/me/identities/
 */
export async function fetchIdentities() {
	log.debug(`Fetching identities from ${COACH_BASE_URL}/user/me/identities`);
	const response = await authFetch(`${COACH_BASE_URL}/user/me/identities`, {});
	if (!response.ok) throw new Error("Failed to fetch identities");
	const data = await response.json();
	log.debug("Successfully fetched identities", data);
	return data;
}

/**
 * Fetch the current authenticated user's chat messages.
 * Calls /user/me/chat-messages/
 */
export async function fetchChatMessages() {
	log.debug("Fetching chat messages from /user/me/chat-messages");
	const response = await authFetch(
		`${COACH_BASE_URL}/user/me/chat-messages`,
		{},
	);
	if (!response.ok) throw new Error("Failed to fetch chat messages");
	const data = await response.json();
	log.debug("Successfully fetched chat messages", data);
	return data;
}

/**
 * Fetch the current authenticated user's actions.
 * Calls /user/me/actions/
 */
export async function fetchActions() {
	log.debug("Fetching actions from /user/me/actions");
	const response = await authFetch(`${COACH_BASE_URL}/user/me/actions`, {});
	if (!response.ok) throw new Error("Failed to fetch actions");
	const data = await response.json();
	log.debug("Successfully fetched actions", data);
	return data;
}

/**
 * Reset (delete) all chat messages for the current authenticated user.
 * Calls /user/me/reset-chat-messages/ (POST)
 * Returns the new chat history (should contain only the initial message, or be empty if none).
 */
export async function resetChatMessages() {
	log.debug("Resetting chat messages via POST /user/me/reset-chat-messages");
	const response = await authFetch(
		`${COACH_BASE_URL}/user/me/reset-chat-messages`,
		{ method: "POST" },
	);
	if (!response.ok) throw new Error("Failed to reset chat messages");
	const data = await response.json();
	log.debug("Successfully reset chat messages", data);
	return data;
}
