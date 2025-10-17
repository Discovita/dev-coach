import React from "react";
import { CoachState } from "@/types/coachState";
import { CoachingPhase } from "@/enums/coachingPhase";
import { Identity } from "@/types/identity";
import {
  getIdentityCategoryColor,
  getIdentityCategoryDisplayName,
  getIdentityCategoryIcon,
  getIdentityCategoryLightColor,
  getIdentityCategoryDarkColor,
} from "@/enums/identityCategory";

const IdentityCard: React.FC<{ identity: Identity }> = ({ identity }) => {
  const IconComponent = getIdentityCategoryIcon(String(identity.category));
  const colorClasses = getIdentityCategoryColor(String(identity.category));
  const categoryDisplayName = getIdentityCategoryDisplayName(
    String(identity.category)
  );

  return (
    <div className="relative p-6">
      {/* Large Icon positioned to the right */}
      <div className="absolute top-1/2 right-6 transform -translate-y-1/2">
        <div className={`p-4 rounded-full ${colorClasses}`}>
          <IconComponent className="w-12 h-12" />
        </div>
      </div>
      
      {/* Content area */}
      <div className="pr-20">
        {/* Header */}
        <div className="mb-4">
          <h3 className={`font-bold text-lg mb-1 ${colorClasses} bg-transparent`}>{identity.name}</h3>
          <p className="text-sm opacity-75 font-medium">{categoryDisplayName}</p>
        </div>

        {/* Affirmation */}
        {identity.affirmation && (
          <div className="mb-4">
            <p className="text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">Affirmation:</p>
            <p className="text-sm italic leading-relaxed bg-white/50 dark:bg-black/20 p-3 rounded-md border-l-4 border-current">
              {identity.affirmation}
            </p>
          </div>
        )}

        {/* Visualization */}
        {identity.visualization && (
          <div className="mb-4">
            <p className="text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">Visualization:</p>
            <p className="text-sm italic leading-relaxed bg-white/50 dark:bg-black/20 p-3 rounded-md border-l-4 border-current">
              {identity.visualization}
            </p>
          </div>
        )}
      </div>
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

  if (!currentIdentity) return null;

  const lightColorClasses = getIdentityCategoryLightColor(String(currentIdentity.category));
  const darkColorClasses = getIdentityCategoryDarkColor(String(currentIdentity.category));

  return (
    <div className={`mb-3 ${lightColorClasses} border-4 rounded-md ${darkColorClasses}`}>
      <IdentityCard identity={currentIdentity} />
    </div>
  );
};
