import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

vi.mock("@/api/auth", () => ({
  getCookie: vi.fn(),
  setCookie: vi.fn(),
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

vi.mock("@/constants/api", () => ({
  COACH_BASE_URL: "http://localhost:8000/api/v1",
  REFRESH: "/token/refresh",
}));

import { authFetch } from "@/utils/authFetch";
import { getCookie, setCookie } from "@/api/auth";

describe("authFetch", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
    vi.mocked(getCookie).mockReturnValue(null);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("makes a fetch request to the given URL", async () => {
    vi.mocked(getCookie).mockImplementation((name: string) => {
      if (name === "neovita-access-token") return "access-123";
      return null;
    });
    vi.mocked(fetch).mockResolvedValue({ status: 200, ok: true } as Response);

    await authFetch("http://localhost:8000/api/v1/user/me");

    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/user/me",
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer access-123",
          "Content-Type": "application/json",
        }),
      })
    );
  });

  it("sets Authorization header when access token exists", async () => {
    vi.mocked(getCookie).mockImplementation((name: string) => {
      if (name === "neovita-access-token") return "my-token";
      return null;
    });
    vi.mocked(fetch).mockResolvedValue({ status: 200, ok: true } as Response);

    await authFetch("http://example.com/api");

    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer my-token",
        }),
      })
    );
  });

  it("does not set Authorization header when no token", async () => {
    vi.mocked(getCookie).mockReturnValue(null);
    vi.mocked(fetch).mockResolvedValue({ status: 200, ok: true } as Response);

    await authFetch("http://example.com/api");

    const callArgs = vi.mocked(fetch).mock.calls[0][1] as RequestInit;
    const headers = callArgs.headers as Record<string, string>;
    expect(headers.Authorization).toBeUndefined();
  });

  it("does not set Content-Type for FormData bodies", async () => {
    vi.mocked(getCookie).mockReturnValue(null);
    vi.mocked(fetch).mockResolvedValue({ status: 200, ok: true } as Response);

    const formData = new FormData();
    formData.append("file", "test");
    await authFetch("http://example.com/api", { body: formData });

    const callArgs = vi.mocked(fetch).mock.calls[0][1] as RequestInit;
    const headers = callArgs.headers as Record<string, string>;
    expect(headers["Content-Type"]).toBeUndefined();
  });

  it("retries with refreshed token on 401", async () => {
    vi.mocked(getCookie).mockImplementation((name: string) => {
      if (name === "neovita-access-token") return "expired-token";
      if (name === "neovita-refresh-token") return "refresh-token";
      return null;
    });

    const refreshResponse = {
      ok: true,
      json: () => Promise.resolve({ access: "new-access-token" }),
    } as Response;

    const failedResponse = { status: 401, ok: false } as Response;
    const successResponse = { status: 200, ok: true } as Response;

    vi.mocked(fetch)
      .mockResolvedValueOnce(failedResponse)
      .mockResolvedValueOnce(refreshResponse)
      .mockResolvedValueOnce(successResponse);

    const result = await authFetch("http://example.com/api");

    expect(result.status).toBe(200);
    expect(setCookie).toHaveBeenCalledWith("neovita-access-token", "new-access-token");
    expect(fetch).toHaveBeenCalledTimes(3);
  });

  it("calls onLogout when refresh fails", async () => {
    vi.mocked(getCookie).mockImplementation((name: string) => {
      if (name === "neovita-access-token") return "expired";
      if (name === "neovita-refresh-token") return "bad-refresh";
      return null;
    });

    const failedResponse = { status: 401, ok: false } as Response;
    const refreshFailResponse = {
      ok: false,
      json: () => Promise.reject(new Error("fail")),
    } as Response;

    vi.mocked(fetch)
      .mockResolvedValueOnce(failedResponse)
      .mockResolvedValueOnce(refreshFailResponse);

    const onLogout = vi.fn();

    await expect(
      authFetch("http://example.com/api", {}, onLogout)
    ).rejects.toThrow();

    expect(onLogout).toHaveBeenCalled();
  });

  it("throws Unauthorized when 401 and no refresh token", async () => {
    vi.mocked(getCookie).mockImplementation((name: string) => {
      if (name === "neovita-access-token") return "token";
      return null;
    });

    vi.mocked(fetch).mockResolvedValue({ status: 401, ok: false } as Response);

    await expect(authFetch("http://example.com/api")).rejects.toThrow(
      "Unauthorized. Please log in."
    );
  });

  it("returns response directly for non-401 status", async () => {
    vi.mocked(getCookie).mockReturnValue(null);
    vi.mocked(fetch).mockResolvedValue({
      status: 200,
      ok: true,
      json: () => Promise.resolve({ data: "test" }),
    } as Response);

    const result = await authFetch("http://example.com/api");
    expect(result.status).toBe(200);
  });
});
