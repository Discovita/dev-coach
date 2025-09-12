import { Action } from "./action";

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
   * List of actions to execute in order. Each item should be an object
   * with 'action' (str) and 'params' (object). Can be sent alongside message.
   */
  actions?: Action[];
}
