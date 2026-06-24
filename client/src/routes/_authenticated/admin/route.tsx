import { useProfile } from "@/hooks/use-profile";
import { Outlet, createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";

/**
 * Admin layout route at /admin.
 *
 * Guards all child routes (e.g. /admin/test, /admin/prompts, /admin/demo)
 * so only admin users can access them. Non-admins are redirected to /chat.
 *
 * Uses isAdminUser() indirectly via useProfile().isAdmin, which is the
 * single source of truth mirroring the backend's IsAdminUser permission.
 */
export const Route = createFileRoute("/_authenticated/admin")({
	component: AdminGuard,
});

function AdminGuard() {
	const { profile, isAdmin, isLoading } = useProfile();
	const navigate = useNavigate();

	useEffect(() => {
		if (isLoading) return;
		if (!profile || !isAdmin) {
			navigate({ to: "/chat" });
		}
	}, [profile, isAdmin, isLoading, navigate]);

	if (isLoading || !profile) {
		return (
			<div className="flex items-center justify-center h-full">
				<span className="text-sm text-muted-foreground">Loading…</span>
			</div>
		);
	}

	if (!isAdmin) return null;

	return <Outlet />;
}
