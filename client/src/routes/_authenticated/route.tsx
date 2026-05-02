import { Outlet, createFileRoute } from "@tanstack/react-router";
import AuthLayout from "@/layout/AuthLayout.tsx";
import { ImpersonationProvider } from "@/providers/ImpersonationProvider";
import { ImpersonationTargetBridge } from "@/components/ImpersonationTargetBridge";

/**
 * Pathless layout route for authenticated pages.
 * - Folder name starts with '_' to exclude from URL path
 * - Wraps child routes in AuthLayout and renders <Outlet />
 * - ImpersonationProvider enables global admin impersonation state
 * - ImpersonationTargetBridge bridges ImpersonationContext → UserTargetProvider
 */
export const Route = createFileRoute("/_authenticated")({
  component: function AuthenticatedLayout() {
    return (
      <ImpersonationProvider>
        <AuthLayout>
          <ImpersonationTargetBridge>
            <Outlet />
          </ImpersonationTargetBridge>
        </AuthLayout>
      </ImpersonationProvider>
    );
  },
});


