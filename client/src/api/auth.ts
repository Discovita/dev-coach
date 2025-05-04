import {
  COACH_BASE_URL,
  USER,
  REGISTER,
  LOGIN,
  FORGOT_PASSWORD,
  RESET_PASSWORD,
} from "@/constants/api";
import { authFetch } from "@/utils/authFetch";
import {
  RegisterCredentials,
  LoginCredentials,
  AuthResponse,
  ResetPasswordCredentials,
} from "@/types/auth";

/**
 * Helper to get a cookie value by name.
 */
export function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(";").shift() ?? null;
  return null;
}

export function setCookie(
  name: string,
  value: string,
  maxAge: number = 60 * 60 * 24
) {
  const cookieOptions = [
    `${name}=${value}`,
    "path=/",
    `max-age=${maxAge}`,
    "SameSite=Lax",
  ];
  if (import.meta.env.MODE === "production") {
    cookieOptions.push("secure");
    if (import.meta.env.VITE_COOKIE_DOMAIN) {
      cookieOptions.push(`domain=${import.meta.env.VITE_COOKIE_DOMAIN}`);
    }
  }
  document.cookie = cookieOptions.join("; ");
}

/**
 * Helper to remove a cookie.
 */
export function removeCookie(name: string) {
  setCookie(name, "", -1);
}

/**
 * Fetch the current authenticated user and profile.
 * Returns AuthResponse with user and profile if authenticated.
 */
export async function fetchUser(): Promise<AuthResponse> {
  const accessToken = getCookie("discovita-access-token");
  if (!accessToken) {
    return { success: false, error: "No access token" };
  }
  const fetchUserUrl = `${COACH_BASE_URL}${USER}`;
  const response = await authFetch(fetchUserUrl, {});
  if (!response.ok) {
    removeCookie("discovita-access-token");
    removeCookie("discovita-refresh-token");
    return { success: false, error: "Not authenticated" };
  }
  return response.json();
}

/**
 * Login with credentials.
 * Sets cookies if successful.
 */
export async function login(userData: LoginCredentials): Promise<AuthResponse> {
  const loginUrl = `${COACH_BASE_URL}${LOGIN}`;
  const response = await fetch(loginUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userData),
  });
  const data: AuthResponse = await response.json();
  if (data.tokens) {
    setCookie("discovita-access-token", data.tokens.access, 60 * 60 * 24);
    setCookie(
      "discovita-refresh-token",
      data.tokens.refresh,
      60 * 60 * 24 * 30
    );
  }
  return data;
}

/**
 * Register a new user.
 * Sets cookies if successful.
 */
export async function register(
  userData: RegisterCredentials
): Promise<AuthResponse> {
  const registerUrl = `${COACH_BASE_URL}${REGISTER}`;
  const response = await fetch(registerUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userData),
  });
  const data: AuthResponse = await response.json();
  if (data.tokens) {
    setCookie("discovita-access-token", data.tokens.access, 60 * 60 * 24);
    setCookie(
      "discovita-refresh-token",
      data.tokens.refresh,
      60 * 60 * 24 * 30
    );
  }
  return data;
}

/**
 * Initiate forgot password flow.
 */
export async function forgotPassword(email: string): Promise<AuthResponse> {
  const forgotPasswordUrl = `${COACH_BASE_URL}${FORGOT_PASSWORD}`;
  const response = await fetch(forgotPasswordUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  return response.json();
}

/**
 * Reset password with token and new password.
 */
export async function resetPassword(
  creds: ResetPasswordCredentials
): Promise<AuthResponse> {
  const resetPasswordUrl = `${COACH_BASE_URL}${RESET_PASSWORD}`;
  const response = await fetch(resetPasswordUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(creds),
  });
  return response.json();
}

/**
 * Log out the user by clearing cookies.
 */
export async function logout(): Promise<void> {
  removeCookie("discovita-access-token");
  removeCookie("discovita-refresh-token");
  // Optionally, you can also call a backend logout endpoint here.
}
