import type { User } from "@/types/user";

/**
 * AccountInformation Component
 * ----------------------------
 * Displays user account information (email, name, member since).
 * Receives profile data as a prop from the parent Account page,
 * which handles impersonation-aware data fetching.
 *
 * Used in: Account page.
 */
export function AccountInformation({ profile }: { profile: User | null }) {
  if (!profile) {
    return (
      <div className="bg-card rounded-lg border p-6">
        <h2 className="text-xl font-medium mb-4">Account Information</h2>
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <div className="bg-card rounded-lg border p-6 space-y-4">
      <h2 className="text-xl font-medium mb-4">Account Information</h2>
      
      <div className="space-y-3">
        <div>
          <label className="text-sm font-medium text-muted-foreground">Email</label>
          <p className="text-base mt-1">{profile.email || "Not available"}</p>
        </div>

        {(profile.first_name || profile.last_name) && (
          <div>
            <label className="text-sm font-medium text-muted-foreground">Name</label>
            <p className="text-base mt-1">
              {[profile.first_name, profile.last_name].filter(Boolean).join(" ") || "Not available"}
            </p>
          </div>
        )}

        {profile.created_at && (
          <div>
            <label className="text-sm font-medium text-muted-foreground">Member since</label>
            <p className="text-base mt-1">
              {new Date(profile.created_at).toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
