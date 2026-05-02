import { useIdentities } from "@/hooks/use-identities";
import { Link, useParams } from "@tanstack/react-router";
import { IdentityState } from "@/enums/identityState";
import {
  getIdentityCategoryDisplayName,
  getIdentityCategoryColor,
  getIdentityCategoryIcon,
} from "@/enums/identityCategory";
import type { Identity } from "@/types/identity";

/**
 * Single Identity Page
 *
 * Purpose:
 * - Displays detailed information about a single identity
 * - Shows large image, title, I AM statement, state, and metadata
 * - Matches Figma design with card-based layout
 */
export default function Identity() {
  const { identityId } = useParams({
    from: "/_authenticated/identities/$identityId",
  });
  const { identities, isLoading, isError } = useIdentities();

  // Find the identity from the cached identities data
  const identity = identities?.find((identity: Identity) => identity.id === identityId);

  /**
   * Format state enum value to a readable display name
   */
  const formatState = (state?: IdentityState): string => {
    if (!state) return "Unknown";
    return state
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  /**
   * Format ISO date string to a readable format
   */
  const formatDate = (dateString?: string): string => {
    if (!dateString) return "N/A";
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateString;
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-[32px] font-bold text-[#1e1e1e]">Identity</h1>
        <div className="text-muted-foreground">Loading identity...</div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="space-y-6">
        <h1 className="text-[32px] font-bold text-[#1e1e1e]">Identity</h1>
        <div className="text-destructive">
          Failed to load identities. Please try again.
        </div>
        <Link
          to="/identities"
          className="text-[color:var(--nv-violet-blue)] underline"
        >
          Back to Identities
        </Link>
      </div>
    );
  }

  if (!identity) {
    return (
      <div className="space-y-6">
        <h1 className="text-[32px] font-bold text-[#1e1e1e]">Identity</h1>
        <div className="text-destructive">Identity not found.</div>
        <Link
          to="/identities"
          className="text-[color:var(--nv-violet-blue)] underline"
        >
          Back to Identities
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 bg-white">
      {/* Back Button */}
      <Link
        to="/identities"
        className="inline-flex items-center gap-2 text-sm text-[color:var(--nv-violet-blue)] hover:underline mb-2"
      >
        <span>←</span>
        <span>Back to Identities</span>
      </Link>

      {/* Large Image Section */}
      <div className="relative overflow-hidden rounded-[16px] w-full aspect-video bg-muted flex items-center justify-center">
        {identity.image?.original ? (
          <img
            src={identity.image.original}
            alt={identity.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="text-center p-4">
            <p className="text-sm text-muted-foreground">Image coming soon</p>
          </div>
        )}
      </div>

      {/* Title, Category, and State Badges */}
      <div className="flex items-center gap-3 flex-wrap">
        <h1 className="text-[32px] font-bold text-[#1e1e1e] leading-none">
          {identity.name}
        </h1>
        {identity.category &&
          (() => {
            const IconComponent = getIdentityCategoryIcon(
              String(identity.category)
            );
            const colorClasses = getIdentityCategoryColor(
              String(identity.category)
            );
            return (
              <span
                className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${colorClasses}`}
              >
                <IconComponent className="w-3 h-3" />
                <span>{getIdentityCategoryDisplayName(identity.category)}</span>
              </span>
            );
          })()}
        {identity.state && (
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
            {formatState(identity.state)}
          </span>
        )}
      </div>

      {/* I AM Statement Section - Always show */}
      <div className="bg-white border border-[#dedede] rounded-[16px] p-[24px] space-y-2">
        <h2 className="text-[20px] font-bold text-[#1e1e1e] leading-none">
          I AM Statement
        </h2>
        {identity.i_am_statement ? (
          <p className="text-[16px] font-normal text-[#1e1e1e]">
            {identity.i_am_statement}
          </p>
        ) : (
          <p className="text-sm text-muted-foreground">I Am coming soon</p>
        )}
      </div>

      {/* Metadata Section (Created/Updated timestamps) - Less prominent */}
      {(identity.created_at || identity.updated_at) && (
        <div className="text-sm text-muted-foreground space-y-1">
          {identity.created_at && (
            <p>Created: {formatDate(identity.created_at)}</p>
          )}
          {identity.updated_at && (
            <p>Updated: {formatDate(identity.updated_at)}</p>
          )}
        </div>
      )}
    </div>
  );
}
