import AdminUsers from "@/pages/admin-users/AdminUsers";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated/admin/users")({
	component: AdminUsers,
});
