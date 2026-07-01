import { CoachingPhase } from "@/enums/coachingPhase";
import {
	getIdentityCategoryColor,
	getIdentityCategoryDarkColor,
	getIdentityCategoryDescription,
	getIdentityCategoryDisplayName,
	getIdentityCategoryIcon,
	getIdentityCategoryLightColor,
} from "@/enums/identityCategory";
import type { CoachState } from "@/types/coachState";
import type { Identity } from "@/types/identity";
import type React from "react";

/**
 * Category info card — mirrors the RefinementBulletin card, but shows the
 * CURRENT identity category (from coachState.identity_focus) and a short
 * description of what that category is. Swaps automatically as the focus
 * changes while the user moves through the categories in brainstorming.
 */
const CategoryInfoCard: React.FC<{ category: string }> = ({ category }) => {
	const IconComponent = getIdentityCategoryIcon(category);
	const colorClasses = getIdentityCategoryColor(category);
	const lightColorClasses = getIdentityCategoryLightColor(category);
	const darkColorClasses = getIdentityCategoryDarkColor(category);
	const displayName = getIdentityCategoryDisplayName(category);
	const description = getIdentityCategoryDescription(category);

	return (
		<div
			className={`mb-3 ${lightColorClasses} border-4 rounded-md ${darkColorClasses}`}
		>
			<div className="p-4">
				<div className="flex items-center gap-2 mb-2">
					<div className={`p-2 rounded-full ${colorClasses}`}>
						<IconComponent className="w-5 h-5" />
					</div>
					<h3 className={`font-bold text-base ${colorClasses} bg-transparent`}>
						{displayName}
					</h3>
				</div>
				<p className="text-sm leading-relaxed opacity-90 m-0">{description}</p>
			</div>
		</div>
	);
};

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
	const phase = coachState?.current_phase;
	const isBrainstorming =
		phase === CoachingPhase.IDENTITY_BRAINSTORMING ||
		phase === CoachingPhase.BRAINSTORMING_REVIEW;
	if (!isBrainstorming) return null;

	const items = identities || [];
	const focus = coachState?.identity_focus;
	// The category card only makes sense while actively brainstorming a category,
	// not during the review recap.
	const showCategoryCard =
		phase === CoachingPhase.IDENTITY_BRAINSTORMING && !!focus;

	return (
		<>
			{showCategoryCard && <CategoryInfoCard category={focus as string} />}
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
							<IdentityBadge
								key={identity.id || identity.name}
								identity={identity}
							/>
						))}
					</div>
				)}
			</div>
		</>
	);
};
