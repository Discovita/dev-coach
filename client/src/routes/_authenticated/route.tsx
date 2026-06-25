import { ImpersonationTargetBridge } from "@/components/ImpersonationTargetBridge";
import AuthLayout from "@/layout/AuthLayout.tsx";
import { ImpersonationProvider } from "@/providers/ImpersonationProvider";
import { Outlet, createFileRoute } from "@tanstack/react-router";

/**
 * Pathless layout route for authenticated pages.
 * - Folder name starts with '_' to exclude from URL path
 * - Wraps child routes in AuthLayout and renders <Outlet />
 * - ImpersonationProvider enables global admin impersonation state
 * - ImpersonationTargetBridge bridges ImpersonationContext → UserTargetProvider
 *
 * The bridge wraps AuthLayout (not just the <Outlet />) so the layout's own
 * impersonation-aware hooks — notably useCoachState, which drives the Studio
 * lock in the sidebar — read the impersonated user's state rather than the
 * logged-in admin's. AuthLayout's other hooks (useProfile for the admin nav,
 * useMeditations for the feature flag) use fixed query keys and are
 * unaffected, so super-admin controls stay visible while impersonating.
 */
export const Route = createFileRoute("/_authenticated")({
	component: function AuthenticatedLayout() {
		return (
			<ImpersonationProvider>
				<ImpersonationTargetBridge>
					<AuthLayout>
						<Outlet />
					</AuthLayout>
				</ImpersonationTargetBridge>
			</ImpersonationProvider>
		);
	},
});
