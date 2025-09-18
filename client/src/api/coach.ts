import { CoachResponse } from "@/types/coachResponse";
import { CoachRequest } from "@/types/coachRequest";
import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";

export class ApiClient {
  /**
   * Send a message to the coach API using authFetch for authentication and token refresh.
   * Calls the /coach/process-message endpoint.
   * @param request - The coach request containing message, model_name, and optional actions
   * @returns CoachResponse from the API
   */
  async sendMessage(request: CoachRequest): Promise<CoachResponse> {
    const response = await authFetch(
      `${COACH_BASE_URL}/coach/process-message`,
      {
        method: "POST",
        body: JSON.stringify(request),
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
  async sendTestScenarioMessage(request: CoachRequest) {
    const response = await authFetch(
      `${COACH_BASE_URL}/coach/process-message-for-user`,
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
    if (!response.ok)
      throw new Error("Failed to send message as test scenario user");
    return response.json();
  }
}

export const apiClient = new ApiClient();
