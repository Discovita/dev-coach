import Login from "@/pages/login/Login.tsx";
import { createFileRoute } from "@tanstack/react-router";

/**
 * /signup index page under pathless _public layout.
 */
export const Route = createFileRoute("/login/")({
	component: Login,
});
