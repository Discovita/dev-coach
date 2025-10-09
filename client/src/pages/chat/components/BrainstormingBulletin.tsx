import React from "react";
import { CoachState } from "@/types/coachState";
import { CoachingPhase } from "@/enums/coachingPhase";
import { Identity } from "@/types/identity";
import { getIdentityCategoryColor } from "@/enums/identityCategory";
import {
  FaDollarSign,
  FaPiggyBank,
  FaUser,
  FaDumbbell,
  FaHeart,
  FaRegCheckSquare,
} from "react-icons/fa";
import { MdFamilyRestroom } from "react-icons/md";
import { BsStars } from "react-icons/bs";
import { AiOutlineSun } from "react-icons/ai";

const CATEGORY_ICON_MAP: Record<
  string,
  React.ComponentType<{ className?: string }>
> = {
  passions_and_talents: BsStars,
  maker_of_money: FaDollarSign,
  keeper_of_money: FaPiggyBank,
  spiritual: AiOutlineSun,
  personal_appearance: FaUser,
  physical_expression: FaDumbbell,
  familial_relations: MdFamilyRestroom,
  romantic_relation: FaHeart,
  doer_of_things: FaRegCheckSquare,
};

const getCategoryIcon = (category: string) => {
  const normalizedCategory = category.toLowerCase();
  if (CATEGORY_ICON_MAP[normalizedCategory]) {
    return CATEGORY_ICON_MAP[normalizedCategory];
  }
  for (const [key, icon] of Object.entries(CATEGORY_ICON_MAP)) {
    if (
      normalizedCategory.includes(key.split("_")[0]) ||
      key.split("_").some((part) => normalizedCategory.includes(part))
    ) {
      return icon;
    }
  }
  return FaUser;
};

const IdentityBadge: React.FC<{ identity: Identity }> = ({ identity }) => {
  const IconComponent = getCategoryIcon(String(identity.category));
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
    coachState?.current_phase === CoachingPhase.IDENTITY_BRAINSTORMING;
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


