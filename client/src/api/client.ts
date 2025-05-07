import { CoachRequest, CoachResponse } from "./types";
import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";

export class ApiClient {
  /**
   * Send a message to the coach API using authFetch for authentication and token refresh.
   * Calls the /coach/process-message endpoint.
   * @param message - The user's message to the coach
   * @param coach_state - The current coach state (optional, depending on backend)
   * @returns CoachResponse from the API
   */
  async sendMessage(
    message: string,
    coach_state: CoachRequest["coach_state"]
  ): Promise<CoachResponse> {
    // Use authFetch to ensure the request is authenticated and tokens are refreshed if needed
    const response = await authFetch(
      `${COACH_BASE_URL}/coach/process-message`,
      {
        method: "POST",
        body: JSON.stringify({
          message,
          coach_state,
        }),
      }
    );
    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }
    return response.json();
  }
}

export const apiClient = new ApiClient();
