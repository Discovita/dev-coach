import { createFileRoute } from "@tanstack/react-router";
import Login from "@/pages/login/Login.tsx";

/**
 * /signup index page under pathless _public layout.
 */
export const Route = createFileRoute("/login/")({
  component: Login,
});
