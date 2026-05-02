import { createFileRoute } from "@tanstack/react-router";
import AdminUsers from "@/pages/admin-users/AdminUsers";

export const Route = createFileRoute("/_authenticated/admin/users")({
  component: AdminUsers,
});
