import ResetPassword from "@/pages/reset-password/ResetPassword.tsx";
import { createFileRoute } from "@tanstack/react-router";

/**
 * /reset-password?token=... — set a new password from an emailed link.
 */
export const Route = createFileRoute("/reset-password/")({
	component: ResetPassword,
});
