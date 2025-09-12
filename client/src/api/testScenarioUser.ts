import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";

/**
 * Fetch profile data for a test scenario user (admin only).
 * Calls /test-user/{userId}/profile/
 */
export async function fetchTestScenarioUserProfile(userId: string) {
  const response = await authFetch(
    `${COACH_BASE_URL}/test-user/${userId}/profile`,
    {}
  );
  if (!response.ok)
    throw new Error("Failed to fetch test scenario user profile");
  return response.json();
}

/**
 * Fetch complete user data for a test scenario user (admin only).
 * Calls /test-user/{userId}/complete/
 */
export async function fetchTestScenarioUserComplete(userId: string) {
  const response = await authFetch(
    `${COACH_BASE_URL}/test-user/${userId}/complete`,
    {}
  );
  if (!response.ok) throw new Error("Failed to fetch test scenario user data");
  return response.json();
}

/**
 * Fetch coach state for a test scenario user (admin only).
 * Calls /test-user/{userId}/coach-state/
 */
export async function fetchTestScenarioUserCoachState(userId: string) {
  const response = await authFetch(
    `${COACH_BASE_URL}/test-user/${userId}/coach-state`,
    {}
  );
  if (!response.ok)
    throw new Error("Failed to fetch test scenario user coach state");
  return response.json();
}

/**
 * Fetch identities for a test scenario user (admin only).
 * Calls /test-user/{userId}/identities/
 */
export async function fetchTestScenarioUserIdentities(userId: string) {
  const response = await authFetch(
    `${COACH_BASE_URL}/test-user/${userId}/identities`,
    {}
  );
  if (!response.ok)
    throw new Error("Failed to fetch test scenario user identities");
  return response.json();
}

/**
 * Fetch actions for a test scenario user (admin only).
 * Calls /test-user/{userId}/actions/
 */
export async function fetchTestScenarioUserActions(userId: string) {
  const response = await authFetch(
    `${COACH_BASE_URL}/test-user/${userId}/actions`,
    {}
  );
  if (!response.ok)
    throw new Error("Failed to fetch test scenario user actions");
  return response.json();
}

/**
 * Fetch chat messages for a test scenario user (admin only).
 * Calls /test-user/{userId}/chat-messages/
 */
export async function fetchTestScenarioChatMessages(userId: string) {
  const response = await authFetch(
    `${COACH_BASE_URL}/test-user/${userId}/chat-messages`,
    {}
  );
  if (!response.ok)
    throw new Error("Failed to fetch test scenario user chat messages");
  return response.json();
}
