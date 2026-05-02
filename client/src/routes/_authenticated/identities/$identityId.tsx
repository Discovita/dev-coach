import { createFileRoute } from "@tanstack/react-router";
import Identity from "@/pages/identities/Identity.tsx";

/**
 * /identities/$identityId dynamic route under pathless _authenticated layout.
 * Matches URLs like /identities/123 where 123 is the identity ID.
 */
export const Route = createFileRoute("/_authenticated/identities/$identityId")({
  component: Identity,
});

