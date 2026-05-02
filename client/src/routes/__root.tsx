import { Outlet, createRootRoute } from "@tanstack/react-router";
import { lazy, Suspense } from "react";
import NotFound from "@/pages/NotFound.tsx";
import { ErrorBoundary } from "@/components/ErrorBoundary";

const TanStackRouterDevtools = import.meta.env.DEV
  ? lazy(() =>
      import("@tanstack/react-router-devtools").then((mod) => ({
        default: mod.TanStackRouterDevtools,
      }))
    )
  : () => null;

/**
 * Root route for TanStack Router file-based routing.
 * - Always matched; renders global wrappers, ErrorBoundary, and Devtools (dev only)
 */
export const Route = createRootRoute({
  component: function Root() {
    return (
      <ErrorBoundary>
        <Outlet />
        <Suspense>
          <TanStackRouterDevtools />
        </Suspense>
      </ErrorBoundary>
    );
  },
  notFoundComponent: NotFound,
});

