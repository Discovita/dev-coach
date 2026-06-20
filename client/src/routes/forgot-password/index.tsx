import { createFileRoute } from "@tanstack/react-router";
import ForgotPassword from "@/pages/forgot-password/ForgotPassword.tsx";

/**
 * /forgot-password — request a password-reset email.
 */
export const Route = createFileRoute("/forgot-password/")({
  component: ForgotPassword,
});
