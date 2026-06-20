import { createFileRoute } from "@tanstack/react-router";
import ResetPassword from "@/pages/reset-password/ResetPassword.tsx";

/**
 * /reset-password?token=... — set a new password from an emailed link.
 */
export const Route = createFileRoute("/reset-password/")({
  component: ResetPassword,
});
