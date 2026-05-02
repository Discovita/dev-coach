import { Outlet, createFileRoute } from "@tanstack/react-router";
import PublicLayout from "@/layout/PublicLayout.tsx";

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
