import IAms from "@/pages/i_ams/IAms";
import { createFileRoute } from "@tanstack/react-router";

/**
 * /identities route under pathless _authenticated layout.
 */
export const Route = createFileRoute("/_authenticated/iams/")({
	component: IAms,
});
