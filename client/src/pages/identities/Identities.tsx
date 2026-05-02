import { useIdentities } from "@/hooks/use-identities";
import type { Identity } from "@/types/identity";
import { Link } from "@tanstack/react-router";

/**
 * Identities Page
 *
 * Purpose:
 * - Displays the user's identities in a grid layout
 * - Shows identity cards with image placeholders and names
 * - Matches Figma design with card-based layout
 */
export default function Identities() {
  const { identities, isLoading, isError } = useIdentities();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-[32px] font-bold text-[#1e1e1e]">Identities</h1>
        <div className="text-muted-foreground">Loading identities...</div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="space-y-6">
        <h1 className="text-[32px] font-bold text-[#1e1e1e]">Identities</h1>
        <div className="text-destructive">
          Failed to load identities. Please try again.
        </div>
      </div>
    );
  }

  if (!identities || identities.length === 0) {
    return (
      <div className="space-y-6">
        <h1 className="text-[32px] font-bold text-[#1e1e1e]">Identities</h1>
        <div className="text-muted-foreground">
          No identities found. Create your first identity to get started.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 bg-white">
      <div className="grid grid-cols-1 gap-6">
        {identities.map((identity: Identity, index: number) => (
          <Link
            key={identity.id || `identity-${index}`}
            to="/identities/$identityId"
            params={{ identityId: identity.id || `identity-${index}` }}
            className="space-y-4 cursor-pointer group"
          >
            {/* Image Card */}
            <div className="relative overflow-hidden rounded-[16px] shadow-[0px_1px_4px_0px_rgba(30,30,30,0.25)] w-full aspect-video bg-muted flex items-center justify-center group-hover:shadow-[0px_4px_12px_0px_rgba(30,30,30,0.3)] transition-shadow">
              {identity.image?.original ? (
                <img
                  src={identity.image.original}
                  alt={identity.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="text-center p-4">
                  <p className="text-sm text-muted-foreground">
                    Image coming soon
                  </p>
                </div>
              )}
            </div>

            {/* Identity Name */}
            <h2 className="text-[20px] font-bold text-[#1e1e1e] leading-none text-center group-hover:text-[color:var(--nv-violet-blue)] transition-colors">
              {identity.name}
            </h2>
          </Link>
        ))}
      </div>
    </div>
  );
}
