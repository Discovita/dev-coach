import { useImpersonation } from "@/context/ImpersonationContext";
import { Eye, X } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * ImpersonationBanner
 *
 * Persistent banner displayed at the top of the main content area when an admin
 * is impersonating another user. Shows the impersonated user's name/email and
 * provides a button to exit impersonation.
 *
 * Rendered inside AuthLayout, above the main content <Outlet />.
 */
export function ImpersonationBanner() {
  const { impersonatedUser, stopImpersonating } = useImpersonation();

  if (!impersonatedUser) return null;

  const displayName =
    impersonatedUser.first_name || impersonatedUser.last_name
      ? `${impersonatedUser.first_name} ${impersonatedUser.last_name}`.trim()
      : impersonatedUser.email;

  return (
    <div className="flex items-center justify-between gap-3 mx-4 sm:mx-6 lg:mx-8 mt-4 sm:mt-6 lg:mt-8 px-4 py-2 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 dark:bg-amber-950 dark:border-amber-800 dark:text-amber-200 flex-shrink-0">
      <div className="flex items-center gap-2 min-w-0">
        <Eye className="w-4 h-4 flex-shrink-0" />
        <span className="text-sm font-medium truncate">
          Viewing as <strong>{displayName}</strong>
        </span>
        {displayName !== impersonatedUser.email && (
          <span className="text-xs text-amber-600 dark:text-amber-400 truncate hidden sm:inline">
            ({impersonatedUser.email})
          </span>
        )}
      </div>
      <Button
        variant="outline"
        size="sm"
        onClick={stopImpersonating}
        className="flex-shrink-0 border-amber-300 text-amber-800 hover:bg-amber-100 dark:border-amber-700 dark:text-amber-200 dark:hover:bg-amber-900"
      >
        <X className="w-3 h-3 mr-1" />
        Exit View
      </Button>
    </div>
  );
}
