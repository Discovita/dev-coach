import { CoachResponse } from "@/types/coachResponse";
import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";

export class ApiClient {
  /**
   * Send a message to the coach API using authFetch for authentication and token refresh.
   * Calls the /coach/process-message endpoint.
   * @param message - The user's message to the coach
   * @param model - The model to use when chatting (optional)
   * @returns CoachResponse from the API
   */
  async sendMessage(message: string, model: string): Promise<CoachResponse> {
    const response = await authFetch(
      `${COACH_BASE_URL}/coach/process-message`,
      {
        method: "POST",
        body: JSON.stringify({
          message,
          model,
        }),
      }
    );
    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }
    return response.json();
  }
  /**
   * Send a message as a test scenario user (admin only).
   * Calls /coach/process-message-for-user
   */
  async sendTestScenarioMessage(
    userId: string,
    message: string,
    model?: string
  ) {
    const response = await authFetch(
      `${COACH_BASE_URL}/coach/process-message-for-user`,
      {
        method: "POST",
        body: JSON.stringify({ user_id: userId, message, model }),
      }
    );
    if (!response.ok)
      throw new Error("Failed to send message as test scenario user");
    return response.json();
  }
}

export const apiClient = new ApiClient();
