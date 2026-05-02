import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  fetchUserProfile,
  fetchUserComplete,
  fetchCoachState,
  fetchIdentities,
  fetchChatMessages,
  fetchActions,
  resetChatMessages,
} from "@/api/user";

vi.mock("@/utils/authFetch", () => ({
  authFetch: vi.fn(),
}));

vi.mock("@/constants/api", () => ({
  COACH_BASE_URL: "http://localhost:8000/api/v1",
}));

vi.mock("@/lib/logger", () => ({
  createLogger: () => ({
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  }),
  LogLevel: { DEBUG: 0 },
}));

import { authFetch } from "@/utils/authFetch";

function mockOkResponse(data: unknown) {
  return {
    ok: true,
    json: () => Promise.resolve(data),
  } as Response;
}

function mockErrorResponse(status = 500) {
  return {
    ok: false,
    status,
  } as Response;
}

describe("user API", () => {
  beforeEach(() => {
    vi.mocked(authFetch).mockReset();
  });

  describe("fetchUserProfile", () => {
    it("calls /user/me and returns data", async () => {
      const mockData = { id: "1", email: "test@test.com" };
      vi.mocked(authFetch).mockResolvedValue(mockOkResponse(mockData));

      const result = await fetchUserProfile();
      expect(result).toEqual(mockData);
      expect(authFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/v1/user/me",
        {}
      );
    });

    it("throws on non-ok response", async () => {
      vi.mocked(authFetch).mockResolvedValue(mockErrorResponse());
      await expect(fetchUserProfile()).rejects.toThrow("Failed to fetch user profile");
    });
  });

  describe("fetchUserComplete", () => {
    it("calls /user/me/complete and returns data", async () => {
      const mockData = { id: "1", email: "test@test.com", identities: [] };
      vi.mocked(authFetch).mockResolvedValue(mockOkResponse(mockData));

      const result = await fetchUserComplete();
      expect(result).toEqual(mockData);
      expect(authFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/v1/user/me/complete",
        {}
      );
    });

    it("throws on non-ok response", async () => {
      vi.mocked(authFetch).mockResolvedValue(mockErrorResponse());
      await expect(fetchUserComplete()).rejects.toThrow("Failed to fetch complete user info");
    });
  });

  describe("fetchCoachState", () => {
    it("calls /user/me/coach-state and returns data", async () => {
      const mockData = { current_phase: "introduction" };
      vi.mocked(authFetch).mockResolvedValue(mockOkResponse(mockData));

      const result = await fetchCoachState();
      expect(result).toEqual(mockData);
      expect(authFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/v1/user/me/coach-state",
        {}
      );
    });

    it("throws on non-ok response", async () => {
      vi.mocked(authFetch).mockResolvedValue(mockErrorResponse());
      await expect(fetchCoachState()).rejects.toThrow("Failed to fetch coach state");
    });
  });

  describe("fetchIdentities", () => {
    it("calls /user/me/identities and returns data", async () => {
      const mockData = [{ id: "1", name: "Explorer" }];
      vi.mocked(authFetch).mockResolvedValue(mockOkResponse(mockData));

      const result = await fetchIdentities();
      expect(result).toEqual(mockData);
      expect(authFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/v1/user/me/identities",
        {}
      );
    });

    it("throws on non-ok response", async () => {
      vi.mocked(authFetch).mockResolvedValue(mockErrorResponse());
      await expect(fetchIdentities()).rejects.toThrow("Failed to fetch identities");
    });
  });

  describe("fetchChatMessages", () => {
    it("calls /user/me/chat-messages and returns data", async () => {
      const mockData = [{ role: "coach", content: "Hi!" }];
      vi.mocked(authFetch).mockResolvedValue(mockOkResponse(mockData));

      const result = await fetchChatMessages();
      expect(result).toEqual(mockData);
      expect(authFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/v1/user/me/chat-messages",
        {}
      );
    });

    it("throws on non-ok response", async () => {
      vi.mocked(authFetch).mockResolvedValue(mockErrorResponse());
      await expect(fetchChatMessages()).rejects.toThrow("Failed to fetch chat messages");
    });
  });

  describe("fetchActions", () => {
    it("calls /user/me/actions and returns data", async () => {
      const mockData = [{ id: "1", action: "create_identity" }];
      vi.mocked(authFetch).mockResolvedValue(mockOkResponse(mockData));

      const result = await fetchActions();
      expect(result).toEqual(mockData);
      expect(authFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/v1/user/me/actions",
        {}
      );
    });

    it("throws on non-ok response", async () => {
      vi.mocked(authFetch).mockResolvedValue(mockErrorResponse());
      await expect(fetchActions()).rejects.toThrow("Failed to fetch actions");
    });
  });

  describe("resetChatMessages", () => {
    it("calls /user/me/reset-chat-messages with POST", async () => {
      const mockData = [{ role: "coach", content: "Welcome back!" }];
      vi.mocked(authFetch).mockResolvedValue(mockOkResponse(mockData));

      const result = await resetChatMessages();
      expect(result).toEqual(mockData);
      expect(authFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/v1/user/me/reset-chat-messages",
        { method: "POST" }
      );
    });

    it("throws on non-ok response", async () => {
      vi.mocked(authFetch).mockResolvedValue(mockErrorResponse());
      await expect(resetChatMessages()).rejects.toThrow("Failed to reset chat messages");
    });
  });
});
