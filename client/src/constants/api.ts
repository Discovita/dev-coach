// Use the VITE_COACH_BASE_URL environment variable if it exists, otherwise default to localhost
export const COACH_BASE_URL = import.meta.env.VITE_COACH_BASE_URL || "http://localhost:8000/api/v1";

export const REGISTER = "/auth/register";
export const LOGIN = "/auth/login";
export const REFRESH = "/token/refresh";
export const USER = "/auth/user";
export const VERIFY_EMAIL = "/auth/verify-email";
export const RESEND_VERIFICATION = "/auth/resend-verification";
export const FORGOT_PASSWORD = "/auth/forgot-password";
export const RESET_PASSWORD = "/auth/reset-password";
export const TEST_SCENARIOS = "/test-scenarios";
