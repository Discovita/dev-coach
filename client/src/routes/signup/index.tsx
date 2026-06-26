import { createFileRoute, redirect } from "@tanstack/react-router";

/**
 * /signup — public self-service registration is disabled (invite-only).
 * Anyone hitting this route is redirected to login; accounts are created
 * only by accepting an invite link (/invite/:token).
 */
export const Route = createFileRoute("/signup/")({
	beforeLoad: () => {
		throw redirect({ to: "/login" });
	},
});
