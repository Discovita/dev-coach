import { createFileRoute } from "@tanstack/react-router";
import Studio from "@/pages/studio/Studio";

/**
 * /studio route under pathless _authenticated layout.
 * Provides identity image generation functionality.
 */
export const Route = createFileRoute("/_authenticated/studio/")({
  component: Studio,
});
