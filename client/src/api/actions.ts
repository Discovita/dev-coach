import { authFetch } from "@/utils/authFetch";
import { Action } from "@/types/action";

/**
 * API functions for Actions endpoints.
 * Used in: Coach state visualizer, action history, debugging tools
 */

/**
 * Get all actions for the current user.
 * Returns actions ordered by timestamp (newest first).
 */
export const getActions = async (): Promise<Action[]> => {
  const response = await authFetch("/api/actions/");
  return response.json();
};

/**
 * Get actions for a specific user (admin only).
 * @param userId - The ID of the user to get actions for
 */
export const getActionsForUser = async (userId: string): Promise<Action[]> => {
  const response = await authFetch(`/api/actions/for-user/?user_id=${userId}`);
  return response.json();
};

/**
 * Get actions triggered by a specific coach message.
 * @param messageId - The ID of the coach message
 */
export const getActionsByCoachMessage = async (messageId: string): Promise<Action[]> => {
  const response = await authFetch(`/api/actions/by-coach-message/?message_id=${messageId}`);
  return response.json();
};

/**
 * Get a specific action by ID.
 * @param actionId - The ID of the action to retrieve
 */
export const getAction = async (actionId: string): Promise<Action> => {
  const response = await authFetch(`/api/actions/${actionId}/`);
  return response.json();
}; 