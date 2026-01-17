import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";
import { UserAppearance } from "@/types/userAppearance";

/**
 * User Appearance API
 * -------------------
 * Functions for fetching and updating user appearance preferences.
 * These settings are stored on the User model and apply to all identity image generations.
 *
 * Endpoints covered:
 * - getUserAppearance:    GET    /api/v1/user/me/ (for current user)
 * - updateUserAppearance:  PATCH  /api/v1/user/me/ (for current user)
 * - getTestUserAppearance: GET    /api/v1/admin/users/{id}/profile/ (for admin/test users)
 * - updateTestUserAppearance: PATCH /api/v1/admin/users/{id}/profile/ (for admin/test users)
 */

/**
 * Get appearance preferences for the current authenticated user.
 * GET /api/v1/user/me/
 * @returns UserAppearance from user profile
 */
export async function getUserAppearance(): Promise<UserAppearance> {
  const response = await authFetch(`${COACH_BASE_URL}/user/me`, {});
  if (!response.ok) throw new Error("Failed to fetch user appearance");
  const data = await response.json();
  return {
    gender: data.gender || null,
    skin_tone: data.skin_tone || null,
    hair_color: data.hair_color || null,
    eye_color: data.eye_color || null,
    height: data.height || null,
    build: data.build || null,
    age_range: data.age_range || null,
  };
}

/**
 * Update appearance preferences for the current authenticated user.
 * PATCH /api/v1/user/me/
 * @param appearance - Partial UserAppearance to update
 * @returns Updated UserAppearance
 */
export async function updateUserAppearance(
  appearance: Partial<UserAppearance>
): Promise<UserAppearance> {
  const response = await authFetch(`${COACH_BASE_URL}/user/me`, {
    method: "PATCH",
    body: JSON.stringify(appearance),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Failed to update user appearance" }));
    throw new Error(error.error || "Failed to update user appearance");
  }
  const data = await response.json();
  return {
    gender: data.gender || null,
    skin_tone: data.skin_tone || null,
    hair_color: data.hair_color || null,
    eye_color: data.eye_color || null,
    height: data.height || null,
    build: data.build || null,
    age_range: data.age_range || null,
  };
}

/**
 * Get appearance preferences for a test scenario user (admin only).
 * GET /api/v1/admin/users/{id}/profile/
 * @param userId - UUID of the user
 * @returns UserAppearance from user profile
 */
export async function getTestUserAppearance(userId: string): Promise<UserAppearance> {
  const response = await authFetch(`${COACH_BASE_URL}/admin/users/${userId}/profile`, {});
  if (!response.ok) throw new Error("Failed to fetch test user appearance");
  const data = await response.json();
  return {
    gender: data.gender || null,
    skin_tone: data.skin_tone || null,
    hair_color: data.hair_color || null,
    eye_color: data.eye_color || null,
    height: data.height || null,
    build: data.build || null,
    age_range: data.age_range || null,
  };
}

/**
 * Update appearance preferences for a test scenario user (admin only).
 * PATCH /api/v1/admin/users/{id}/profile/
 * @param userId - UUID of the user
 * @param appearance - Partial UserAppearance to update
 * @returns Updated UserAppearance
 */
export async function updateTestUserAppearance(
  userId: string,
  appearance: Partial<UserAppearance>
): Promise<UserAppearance> {
  const response = await authFetch(`${COACH_BASE_URL}/admin/users/${userId}/profile`, {
    method: "PATCH",
    body: JSON.stringify(appearance),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Failed to update test user appearance" }));
    throw new Error(error.error || "Failed to update test user appearance");
  }
  const data = await response.json();
  return {
    gender: data.gender || null,
    skin_tone: data.skin_tone || null,
    hair_color: data.hair_color || null,
    eye_color: data.eye_color || null,
    height: data.height || null,
    build: data.build || null,
    age_range: data.age_range || null,
  };
}
