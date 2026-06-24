import Dashboard from "@/pages/dashboard/Dashboard.tsx";
import { createFileRoute } from "@tanstack/react-router";

/**
 * /dashboard index page under pathless _authenticated layout.
 */
export const Route = createFileRoute("/_authenticated/dashboard/")({
	component: Dashboard,
});
