import InviteRegister from "@/pages/invite/InviteRegister.tsx";
import { createFileRoute } from "@tanstack/react-router";

/**
 * /invite/:token — the only entry to the register form. Validates the magic
 * link and, if valid, reveals a register form with the invited email locked.
 */
export const Route = createFileRoute("/invite/$token")({
	component: function InviteRoute() {
		const { token } = Route.useParams();
		return <InviteRegister token={token} />;
	},
});
