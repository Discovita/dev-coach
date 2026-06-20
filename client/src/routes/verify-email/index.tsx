import { createFileRoute } from "@tanstack/react-router";
import VerifyEmail from "@/pages/verify-email/VerifyEmail.tsx";

/**
 * /verify-email?token=... — confirm an email address from an emailed link.
 */
export const Route = createFileRoute("/verify-email/")({
  component: VerifyEmail,
});
