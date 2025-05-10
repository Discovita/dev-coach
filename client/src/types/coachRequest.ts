/**
 * Request model for coach API.
 */
export interface CoachRequest {
  /**
   * User's message
   */
  message: string;
  model?: string;
}
