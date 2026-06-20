import { createFileRoute } from "@tanstack/react-router";
import CheckEmail from "@/pages/check-email/CheckEmail.tsx";

/**
 * /check-email?email=... — post-registration "verify your email" pause page.
 */
export const Route = createFileRoute("/check-email/")({
  validateSearch: (search: Record<string, unknown>): { email?: string } => ({
    email: typeof search.email === "string" ? search.email : undefined,
  }),
  component: CheckEmail,
});
