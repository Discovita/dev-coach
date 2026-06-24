import { ApiClient } from "@/api/coach";
import type { CoachRequest } from "@/types/coachRequest";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/utils/authFetch", () => ({
	authFetch: vi.fn(),
}));

vi.mock("@/constants/api", () => ({
	COACH_BASE_URL: "http://localhost:8000/api/v1",
}));

import { authFetch } from "@/utils/authFetch";

describe("ApiClient", () => {
	let client: ApiClient;

	beforeEach(() => {
		client = new ApiClient();
		vi.mocked(authFetch).mockReset();
	});

	describe("sendMessage", () => {
		it("calls the correct endpoint with POST", async () => {
			vi.mocked(authFetch).mockResolvedValue({
				ok: true,
				json: () => Promise.resolve({ message: "Hello!" }),
			} as Response);

			const request: CoachRequest = { message: "Hi coach" };
			await client.sendMessage(request);

			expect(authFetch).toHaveBeenCalledWith(
				"http://localhost:8000/api/v1/coach/process-message",
				expect.objectContaining({
					method: "POST",
					body: JSON.stringify(request),
				}),
			);
		});

		it("returns the parsed response on success", async () => {
			const mockResponse = { message: "Welcome!", component: null };
			vi.mocked(authFetch).mockResolvedValue({
				ok: true,
				json: () => Promise.resolve(mockResponse),
			} as Response);

			const result = await client.sendMessage({ message: "Hello" });
			expect(result).toEqual(mockResponse);
		});

		it("throws on non-ok response", async () => {
			vi.mocked(authFetch).mockResolvedValue({
				ok: false,
				statusText: "Internal Server Error",
			} as Response);

			await expect(client.sendMessage({ message: "Hi" })).rejects.toThrow(
				"API request failed: Internal Server Error",
			);
		});
	});

	describe("sendTestScenarioMessage", () => {
		it("calls the admin endpoint", async () => {
			vi.mocked(authFetch).mockResolvedValue({
				ok: true,
				json: () => Promise.resolve({ message: "Admin response" }),
			} as Response);

			const request: CoachRequest = { message: "Test", user_id: "user-123" };
			await client.sendTestScenarioMessage(request);

			expect(authFetch).toHaveBeenCalledWith(
				"http://localhost:8000/api/v1/admin/coach/process-message-for-user",
				expect.objectContaining({
					method: "POST",
					body: JSON.stringify(request),
				}),
			);
		});

		it("throws on non-ok response", async () => {
			vi.mocked(authFetch).mockResolvedValue({
				ok: false,
			} as Response);

			await expect(
				client.sendTestScenarioMessage({ message: "Test" }),
			).rejects.toThrow("Failed to send message as specific user");
		});
	});
});
