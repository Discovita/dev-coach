import { Link } from "@tanstack/react-router";

/**
 * Dashboard
 *
 * Purpose:
 * - Simple dashboard page after login showing overview of user's account and activity.
 *
 * Notes:
 * - Clean, minimal design with placeholder content.
 */
export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back! Here's an overview of your account.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Identities Card */}
        <Link
          to="/identities"
          className="bg-card rounded-lg border p-6 hover:border-[color:var(--nv-violet-blue)] hover:shadow-md transition-all cursor-pointer block"
        >
          <h2 className="text-xl font-medium mb-2">Identities</h2>
          <p className="text-sm text-muted-foreground mb-4">
            Manage your identity profiles and explore new ones.
          </p>
          <div className="text-2xl font-semibold">—</div>
        </Link>
      </div>
    </div>
  );
}
