import { ComponentAction } from "./componentConfig";

/**
 * Request model for coach API.
 */
export interface CoachRequest {
  /**
   * User's message
   */
  message: string;
  /**
   * Optional model name. If not provided, uses default.
   */
  model_name?: string;
  /**
   * Optional user ID (UUID) to act as (admin only). If not provided, uses request.user.
   */
  user_id?: string;
  /**
   * List of actions to execute in order. Each item should be an object
   * with 'action' (str) and 'params' (object). Can be sent alongside message.
   */
  actions?: ComponentAction[];
}
