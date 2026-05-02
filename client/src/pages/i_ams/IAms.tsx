import { useIdentities } from "@/hooks/use-identities";
import type { Identity } from "@/types/identity";
import { Link } from "@tanstack/react-router";
import { getArticle } from "@/utils/getArticle";

/**
 * I Am's Page
 *
 * Purpose:
 * - Displays the user's identities in a grid layout
 * - Shows identity cards with image placeholders and names
 * - Matches Figma design with card-based layout
 */

const DEFAULT_I_AM_STATEMENT =
  "This identity doesn't have an I Am statement yet. Continue coaching to craft one.";

export default function IAms() {
  const { identities, isLoading, isError } = useIdentities();

  if (isLoading) {
    return <div className="text-muted-foreground">Loading identities...</div>;
  }

  if (isError) {
    return (
      <div className="text-destructive">
        Failed to load identities. Please try again.
      </div>
    );
  }

  if (!identities || identities.length === 0) {
    return (
      <div className="text-muted-foreground">
        No identities found. Create your first identity to get started.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-[32px] bg-white">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[32px]">
        {identities.map((identity: Identity, index: number) => (
          <Link
            key={identity.id || `identity-${index}`}
            to="/identities/$identityId"
            params={{ identityId: identity.id || `identity-${index}` }}
            className="flex flex-col gap-[24px] cursor-pointer group"
          >
            {/* Image Card */}
            <div className="relative overflow-hidden rounded-[16px] shadow-[0px_1px_4px_0px_rgba(30,30,30,0.25)] w-full aspect-video bg-muted flex items-center justify-center group-hover:shadow-[0px_4px_12px_0px_rgba(30,30,30,0.3)] transition-shadow">
              {identity.image?.large ? (
                <img
                  src={identity.image.large}
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

            {/* Identity Name and Description */}
            <div className="flex flex-col gap-[8px] leading-none text-[#1e1e1e]">
              <h2 className="text-[20px] md:text-[24px] font-semibold group-hover:text-[color:var(--nv-violet-blue)] transition-colors">
                I am {getArticle(identity.name)} {identity.name}
              </h2>
              <p className="text-[14px] md:text-[16px] font-normal">
                {identity.i_am_statement || DEFAULT_I_AM_STATEMENT}
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
