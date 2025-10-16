import React from "react";
import { CoachState } from "@/types/coachState";
import { CoachingPhase } from "@/enums/coachingPhase";
import { Identity } from "@/types/identity";
import { 
  getIdentityCategoryColor, 
  getIdentityCategoryDisplayName,
  getIdentityCategoryIcon 
} from "@/enums/identityCategory";

const IdentityCard: React.FC<{ identity: Identity }> = ({ identity }) => {
  const IconComponent = getIdentityCategoryIcon(String(identity.category));
  const colorClasses = getIdentityCategoryColor(String(identity.category));
  const categoryDisplayName = getIdentityCategoryDisplayName(String(identity.category));
  
  return (
    <div className={`p-4 rounded-lg border ${colorClasses}`}>
      <div className="flex items-center gap-2 mb-3">
        <IconComponent className="w-5 h-5" />
        <div>
          <h3 className="font-semibold text-sm">{identity.name}</h3>
          <p className="text-xs opacity-75">{categoryDisplayName}</p>
        </div>
      </div>
      
      {identity.affirmation && (
        <div className="mb-3">
          <p className="text-xs font-medium mb-1">Affirmation:</p>
          <p className="text-xs italic">{identity.affirmation}</p>
        </div>
      )}
      
      {identity.visualization && (
        <div className="mb-3">
          <p className="text-xs font-medium mb-1">Visualization:</p>
          <p className="text-xs italic">{identity.visualization}</p>
        </div>
      )}
      
      {identity.notes && identity.notes.length > 0 && (
        <div>
          <p className="text-xs font-medium mb-1">Notes:</p>
          <ul className="text-xs space-y-1">
            {identity.notes.map((note, index) => (
              <li key={index} className="flex items-start gap-1">
                <span className="text-xs">•</span>
                <span>{note}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export const RefinementBulletin: React.FC<{
  coachState: CoachState | null | undefined;
}> = ({ coachState }) => {
  const isRefinement =
    coachState?.current_phase === CoachingPhase.IDENTITY_REFINEMENT;
  
  if (!isRefinement) return null;

  const currentIdentity = coachState?.current_identity;

  return (
    <div className="mb-3 p-3 bg-indigo-100 dark:bg-neutral-800 border border-indigo-400 rounded-md">
      <div className="flex items-center justify-between mb-3">
        <div className="text-xs font-semibold text-indigo-800 dark:text-indigo-200">
          Current Identity for Refinement
        </div>
      </div>
      
      {!currentIdentity ? (
        <p className="text-xs italic text-neutral-500 dark:text-neutral-400 m-0">
          No identity selected for refinement.
        </p>
      ) : (
        <IdentityCard identity={currentIdentity} />
      )}
    </div>
  );
};
