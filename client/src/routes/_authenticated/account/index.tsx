import Account from "@/pages/account/Account.tsx";
import { createFileRoute } from "@tanstack/react-router";

/**
 * /account route under pathless _authenticated layout.
 */
export const Route = createFileRoute("/_authenticated/account/")({
	component: Account,
});
