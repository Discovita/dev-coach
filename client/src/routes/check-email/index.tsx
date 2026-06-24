import CheckEmail from "@/pages/check-email/CheckEmail.tsx";
import { createFileRoute } from "@tanstack/react-router";

/**
 * /check-email?email=... — post-registration "verify your email" pause page.
 */
export const Route = createFileRoute("/check-email/")({
	validateSearch: (search: Record<string, unknown>): { email?: string } => ({
		email: typeof search.email === "string" ? search.email : undefined,
	}),
	component: CheckEmail,
});
