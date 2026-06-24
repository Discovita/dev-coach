import ForgotPassword from "@/pages/forgot-password/ForgotPassword.tsx";
import { createFileRoute } from "@tanstack/react-router";

/**
 * /forgot-password — request a password-reset email.
 */
export const Route = createFileRoute("/forgot-password/")({
	component: ForgotPassword,
});
