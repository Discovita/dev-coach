import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";

/**
 * Fetch the current authenticated user's profile (basic info only).
 * Calls /user/me/
 */
export async function fetchUserProfile() {
  const response = await authFetch(`${COACH_BASE_URL}/user/me`, {});
  if (!response.ok) throw new Error("Failed to fetch user profile");
  return response.json();
}

/**
 * Fetch the current authenticated user's complete info (all nested data).
 * Calls /user/me/complete/
 */
export async function fetchUserComplete() {
  const response = await authFetch(`${COACH_BASE_URL}/user/me/complete`, {});
  if (!response.ok) throw new Error("Failed to fetch complete user info");
  return response.json();
}

/**
 * Fetch the current authenticated user's coach state.
 * Calls /user/me/coach-state/
 */
export async function fetchCoachState() {
  const response = await authFetch(`${COACH_BASE_URL}/user/me/coach-state`, {});
  if (!response.ok) throw new Error("Failed to fetch coach state");
  return response.json();
}

/**
 * Fetch the current authenticated user's identities.
 * Calls /user/me/identities/
 */
export async function fetchIdentities() {
  const response = await authFetch(`${COACH_BASE_URL}/user/me/identities`, {});
  if (!response.ok) throw new Error("Failed to fetch identities");
  return response.json();
}

/**
 * Fetch the current authenticated user's chat messages.
 * Calls /user/me/chat-messages/
 */
export async function fetchChatMessages() {
  const response = await authFetch(
    `${COACH_BASE_URL}/user/me/chat-messages`,
    {}
  );
  if (!response.ok) throw new Error("Failed to fetch chat messages");
  return response.json();
}

/**
 * Fetch the current authenticated user's actions.
 * Calls /user/me/actions/
 */
export async function fetchActions() {
  const response = await authFetch(`${COACH_BASE_URL}/user/me/actions`, {});
  if (!response.ok) throw new Error("Failed to fetch actions");
  return response.json();
}

/**
 * Reset (delete) all chat messages for the current authenticated user.
 * Calls /user/me/reset-chat-messages/ (POST)
 * Returns the new chat history (should contain only the initial message, or be empty if none).
 */
export async function resetChatMessages() {
  const response = await authFetch(
    `${COACH_BASE_URL}/user/me/reset-chat-messages`,
    { method: "POST" }
  );
  if (!response.ok) throw new Error("Failed to reset chat messages");
  return response.json();
}
