import React from "react";
import { CoachState } from "@/types/coachState";
import { CoachingPhase } from "@/enums/coachingPhase";
import { Identity } from "@/types/identity";
import { getIdentityCategoryColor, getIdentityCategoryIcon } from "@/enums/identityCategory";

const IdentityBadge: React.FC<{ identity: Identity }> = ({ identity }) => {
  const IconComponent = getIdentityCategoryIcon(String(identity.category));
  const colorClasses = getIdentityCategoryColor(String(identity.category));
  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${colorClasses}`}
    >
      <IconComponent className="w-3 h-3" />
      <span className="font-medium">{identity.name}</span>
    </div>
  );
};

export const BrainstormingBulletin: React.FC<{
  coachState: CoachState | null | undefined;
  identities: Identity[] | null | undefined;
}> = ({ coachState, identities }) => {
  const isBrainstorming =
    coachState?.current_phase === CoachingPhase.IDENTITY_BRAINSTORMING ||
    coachState?.current_phase === CoachingPhase.BRAINSTORMING_REVIEW;
  if (!isBrainstorming) return null;

  const items = identities || [];

  return (
    <div className="mb-3 p-3 bg-gold-100 dark:bg-neutral-800 border border-gold-400 rounded-md">
      <div className="flex items-center justify-between mb-2">
        <div className="text-xs font-semibold text-gold-800 dark:text-gold-200">
          Identities
        </div>
        <div className="text-[10px] text-neutral-500 dark:text-neutral-400">
          {items.length} total
        </div>
      </div>
      {items.length === 0 ? (
        <p className="text-xs italic text-neutral-500 dark:text-neutral-400 m-0">
          No identities created yet.
        </p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {items.map((identity) => (
            <IdentityBadge key={identity.id || identity.name} identity={identity} />
          ))}
        </div>
      )}
    </div>
  );
};


