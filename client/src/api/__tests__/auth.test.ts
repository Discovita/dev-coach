import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { getCookie, setCookie, removeCookie, login, register, logout } from "@/api/auth";

vi.mock("@/api/user", () => ({
  fetchUserComplete: vi.fn().mockResolvedValue({ id: "user-1", email: "test@test.com" }),
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

let cookieStore = "";
const cookieDescriptor = Object.getOwnPropertyDescriptor(Document.prototype, "cookie") ||
  Object.getOwnPropertyDescriptor(HTMLDocument.prototype, "cookie");

beforeEach(() => {
  cookieStore = "";
  if (cookieDescriptor) {
    Object.defineProperty(document, "cookie", {
      configurable: true,
      get: () => cookieStore,
      set: (val: string) => { cookieStore = val; },
    });
  }
});

afterEach(() => {
  if (cookieDescriptor) {
    Object.defineProperty(document, "cookie", cookieDescriptor);
  }
});

describe("cookie helpers", () => {
  describe("getCookie", () => {
    it("returns null when cookie does not exist", () => {
      cookieStore = "";
      expect(getCookie("missing")).toBeNull();
    });

    it("returns the cookie value when it exists", () => {
      cookieStore = "neovita-access-token=abc123; path=/";
      expect(getCookie("neovita-access-token")).toBe("abc123");
    });

    it("handles multiple cookies", () => {
      cookieStore = "a=1; b=2; c=3";
      expect(getCookie("b")).toBe("2");
    });
  });

  describe("setCookie", () => {
    it("sets a cookie with default maxAge", () => {
      setCookie("test-cookie", "value123");
      expect(cookieStore).toContain("test-cookie=value123");
      expect(cookieStore).toContain("path=/");
      expect(cookieStore).toContain("max-age=86400");
    });

    it("sets a cookie with custom maxAge", () => {
      setCookie("test-cookie", "value", 3600);
      expect(cookieStore).toContain("max-age=3600");
    });
  });

  describe("removeCookie", () => {
    it("sets max-age to -1 to remove the cookie", () => {
      removeCookie("test-cookie");
      expect(cookieStore).toContain("max-age=-1");
    });
  });
});

describe("login", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn()
    );
    Object.defineProperty(document, "cookie", {
      writable: true,
      value: "",
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("returns auth response with tokens on success", async () => {
    const mockResponse = {
      success: true,
      tokens: { access: "access-token", refresh: "refresh-token" },
    };
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    } as Response);

    const result = await login({ email: "test@test.com", password: "password" });
    expect(result.success).toBe(true);
    expect(result.tokens).toBeDefined();
  });

  it("sets cookies on successful login with tokens", async () => {
    const cookiesSet: string[] = [];
    Object.defineProperty(document, "cookie", {
      configurable: true,
      get: () => cookiesSet.join("; "),
      set: (val: string) => { cookiesSet.push(val); },
    });

    const mockResponse = {
      success: true,
      tokens: { access: "access-123", refresh: "refresh-456" },
    };
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    } as Response);

    await login({ email: "test@test.com", password: "password" });
    const allCookies = cookiesSet.join(" | ");
    expect(allCookies).toContain("neovita-access-token=access-123");
    expect(allCookies).toContain("neovita-refresh-token=refresh-456");
  });

  it("returns parsed JSON error when response is not ok", async () => {
    const errorBody = JSON.stringify({ success: false, error: "Bad credentials" });
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 401,
      text: () => Promise.resolve(errorBody),
    } as Response);

    const result = await login({ email: "test@test.com", password: "wrong" });
    expect(result.success).toBe(false);
    expect(result.error).toBe("Bad credentials");
  });

  it("throws when response is not ok and body is not JSON", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 500,
      text: () => Promise.resolve("Internal Server Error"),
    } as Response);

    await expect(
      login({ email: "test@test.com", password: "password" })
    ).rejects.toThrow("Login failed with status 500");
  });

  it("sends correct request payload", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    } as Response);

    await login({ email: "user@example.com", password: "secret" });

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/auth/login"),
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "user@example.com", password: "secret" }),
      })
    );
  });
});

describe("register", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
    Object.defineProperty(document, "cookie", {
      writable: true,
      value: "",
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("returns auth response on success", async () => {
    const mockResponse = {
      success: true,
      tokens: { access: "access-token", refresh: "refresh-token" },
    };
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    } as Response);

    const result = await register({ email: "new@test.com", password: "password" });
    expect(result.success).toBe(true);
  });

  it("throws on non-JSON error body", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 500,
      text: () => Promise.resolve("Server Error"),
    } as Response);

    await expect(
      register({ email: "new@test.com", password: "password" })
    ).rejects.toThrow("Registration failed with status 500");
  });
});

describe("logout", () => {
  it("clears auth cookies", async () => {
    Object.defineProperty(document, "cookie", {
      writable: true,
      value: "neovita-access-token=abc; neovita-refresh-token=def",
    });

    await logout();
    expect(document.cookie).toContain("max-age=-1");
  });
});
