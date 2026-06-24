import Identities from "@/pages/identities/Identities.tsx";
import { createFileRoute } from "@tanstack/react-router";

/**
 * /identities route under pathless _authenticated layout.
 */
export const Route = createFileRoute("/_authenticated/identities/")({
	component: Identities,
});
