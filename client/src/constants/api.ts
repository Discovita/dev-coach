// Use the VITE_COACH_BASE_URL environment variable if it exists, otherwise default to localhost
export const COACH_BASE_URL =
	import.meta.env.VITE_COACH_BASE_URL || "http://localhost:8000/api/v1";

export const REGISTER = "/auth/register";
export const LOGIN = "/auth/login";
export const REFRESH = "/token/refresh";
export const USER = "/auth/user";
export const VERIFY_EMAIL = "/auth/verify-email";
export const RESEND_VERIFICATION = "/auth/resend-verification";
export const FORGOT_PASSWORD = "/auth/forgot-password";
export const RESET_PASSWORD = "/auth/reset-password";
export const VALIDATE_INVITE = "/auth/invites"; // GET /auth/invites/{token}
export const REGISTER_VIA_INVITE = "/auth/register-via-invite";
export const ADMIN_INVITES = "/admin/invites";
export const TEST_SCENARIOS = "/admin/test-scenarios";
export const FREEZE_SESSION = "/admin/test-scenarios/freeze-session";
