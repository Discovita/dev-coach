import { createFileRoute } from "@tanstack/react-router";
import IAms from "@/pages/i_ams/IAms";

/**
 * /identities route under pathless _authenticated layout.
 */
export const Route = createFileRoute("/_authenticated/iams/")({
  component: IAms,
});
