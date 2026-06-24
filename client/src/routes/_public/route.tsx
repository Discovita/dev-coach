import PublicLayout from "@/layout/PublicLayout.tsx";
import { Outlet, createFileRoute } from "@tanstack/react-router";

/**
 * Pathless layout for public pages that should use the shared PublicLayout
 * (header/footer, constrained viewport). Folder name starts with '_' so it
 * doesn't appear in the URL.
 */
export const Route = createFileRoute("/_public")({
	component: function PublicLayoutRoute() {
		return (
			<PublicLayout>
				<Outlet />
			</PublicLayout>
		);
	},
});
