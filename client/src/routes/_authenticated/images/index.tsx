import { createFileRoute } from "@tanstack/react-router";
import Images from "@/pages/images/Images";

/**
 * /images route under pathless _authenticated layout.
 * Provides identity image generation functionality.
 */
export const Route = createFileRoute("/_authenticated/images/")({
  component: Images,
});
