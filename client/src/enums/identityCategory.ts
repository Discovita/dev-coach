import type React from "react";
import { AiOutlineSun } from "react-icons/ai";
import { BsStars } from "react-icons/bs";
import {
	FaDollarSign,
	FaDumbbell,
	FaHeart,
	FaPiggyBank,
	FaRegCheckSquare,
	FaUser,
} from "react-icons/fa";
import { MdFamilyRestroom } from "react-icons/md";

/**
 * Represents the category of an identity.
 * This enum is used to classify identities within the application,
 * for example, in the `Identity` interface in `client/src/types/identity.ts`.
 */
export enum IdentityCategory {
	PASSIONS_AND_TALENTS = "passions_and_talents",
	MAKER_OF_MONEY = "maker_of_money",
	KEEPER_OF_MONEY = "keeper_of_money",
	SPIRITUAL = "spiritual",
	PERSONAL_APPEARANCE = "personal_appearance",
	PHYSICAL_EXPRESSION = "physical_expression",
	FAMILIAL_RELATIONS = "familial_relations",
	ROMANTIC_RELATION = "romantic_relation",
	DOER_OF_THINGS = "doer_of_things",
}

/**
 * Maps identity category values to their human-readable display names
 */
export const IDENTITY_CATEGORY_DISPLAY_NAMES: Record<IdentityCategory, string> =
	{
		[IdentityCategory.PASSIONS_AND_TALENTS]: "Passions and Talents",
		[IdentityCategory.MAKER_OF_MONEY]: "Maker of Money",
		[IdentityCategory.KEEPER_OF_MONEY]: "Keeper of Money",
		[IdentityCategory.SPIRITUAL]: "Spiritual",
		[IdentityCategory.PERSONAL_APPEARANCE]: "Personal Appearance",
		[IdentityCategory.PHYSICAL_EXPRESSION]: "Physical Expression",
		[IdentityCategory.FAMILIAL_RELATIONS]: "Familial Relations",
		[IdentityCategory.ROMANTIC_RELATION]: "Romantic Relation",
		[IdentityCategory.DOER_OF_THINGS]: "Doer of Things",
	};

/**
 * Maps identity category values to a short description of what the category is.
 * Rendered in the brainstorming bulletin above the composer; sourced from the
 * coach docs (coach/identity-categories.md). Descriptive, not addressed to the
 * user.
 */
export const IDENTITY_CATEGORY_DESCRIPTIONS: Record<IdentityCategory, string> =
	{
		[IdentityCategory.PASSIONS_AND_TALENTS]:
			"The foundational traits, skills, and interests that make a person uniquely themselves — their personality and gifts, like Musician, Designer, or Meticulous Executor. The one category that can hold several identities.",
		[IdentityCategory.MAKER_OF_MONEY]:
			"The identity a person channels energy through to generate income — money being a necessity, not a career. About who actually earns, which is often different from the passion or the job title.",
		[IdentityCategory.KEEPER_OF_MONEY]:
			"A separate energy from earning — the identity that keeps, manages, and grows money and defines the kind of financial life a person wants. Empowered and expansive (Wise Steward, Empire Builder), not fearful bean-counting.",
		[IdentityCategory.SPIRITUAL]:
			"A person's relationship to something greater than themselves — transcendence, meaning, and connection. Not limited to religion; it can be philosophical, ancient, meditative, or wholly their own (Universe's Child, Mystical Healer).",
		[IdentityCategory.PERSONAL_APPEARANCE]:
			"How a person presents to the world — style, grooming, home environment, and overall aesthetic presence. A reflection of self-worth and self-care, not vanity.",
		[IdentityCategory.PHYSICAL_EXPRESSION]:
			"A person's relationship with their body — the vessel they live in — and how they tend its vitality through movement, fuel, and care. Distinct from appearance, which is presentation.",
		[IdentityCategory.FAMILIAL_RELATIONS]:
			"How a person shows up across their family — biological, chosen, or symbolic. Can be literal (Mother, Brother) or archetypal (Family Anchor, Generational Healer), and one energy or several.",
		[IdentityCategory.ROMANTIC_RELATION]:
			"The identity for intimate partnership, sexuality, and romantic energy — how a person aspires to show up in love, at any relationship status. Aspirational, not a description of current behavior.",
		[IdentityCategory.DOER_OF_THINGS]:
			'The identity behind executive function — bringing visions into reality and handling life\'s necessities as self-affirming action rather than burdens. An elevating name like Captain of My Life, not "the dishwasher."',
	};

/**
 * Maps identity category values to their color classes for badges
 */
export const IDENTITY_CATEGORY_COLORS: Record<IdentityCategory, string> = {
	[IdentityCategory.PASSIONS_AND_TALENTS]:
		"bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
	[IdentityCategory.MAKER_OF_MONEY]:
		"bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
	[IdentityCategory.KEEPER_OF_MONEY]:
		"bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
	[IdentityCategory.SPIRITUAL]:
		"bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
	[IdentityCategory.PERSONAL_APPEARANCE]:
		"bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200",
	[IdentityCategory.PHYSICAL_EXPRESSION]:
		"bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
	[IdentityCategory.FAMILIAL_RELATIONS]:
		"bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200",
	[IdentityCategory.ROMANTIC_RELATION]:
		"bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
	[IdentityCategory.DOER_OF_THINGS]:
		"bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200",
};

/**
 * Maps identity category values to their light background colors for cards
 */
export const IDENTITY_CATEGORY_LIGHT_COLORS: Record<IdentityCategory, string> =
	{
		[IdentityCategory.PASSIONS_AND_TALENTS]: "bg-orange-50 dark:bg-orange-950",
		[IdentityCategory.MAKER_OF_MONEY]: "bg-green-50 dark:bg-green-950",
		[IdentityCategory.KEEPER_OF_MONEY]: "bg-emerald-50 dark:bg-emerald-950",
		[IdentityCategory.SPIRITUAL]: "bg-purple-50 dark:bg-purple-950",
		[IdentityCategory.PERSONAL_APPEARANCE]: "bg-pink-50 dark:bg-pink-950",
		[IdentityCategory.PHYSICAL_EXPRESSION]: "bg-blue-50 dark:bg-blue-950",
		[IdentityCategory.FAMILIAL_RELATIONS]: "bg-indigo-50 dark:bg-indigo-950",
		[IdentityCategory.ROMANTIC_RELATION]: "bg-red-50 dark:bg-red-950",
		[IdentityCategory.DOER_OF_THINGS]: "bg-teal-50 dark:bg-teal-950",
	};

/**
 * Maps identity category values to their dark colors for borders, text, and icons
 */
export const IDENTITY_CATEGORY_DARK_COLORS: Record<IdentityCategory, string> = {
	[IdentityCategory.PASSIONS_AND_TALENTS]:
		"border-orange-300 text-orange-800 dark:border-orange-600 dark:text-orange-200",
	[IdentityCategory.MAKER_OF_MONEY]:
		"border-green-300 text-green-800 dark:border-green-600 dark:text-green-200",
	[IdentityCategory.KEEPER_OF_MONEY]:
		"border-emerald-300 text-emerald-800 dark:border-emerald-600 dark:text-emerald-200",
	[IdentityCategory.SPIRITUAL]:
		"border-purple-300 text-purple-800 dark:border-purple-600 dark:text-purple-200",
	[IdentityCategory.PERSONAL_APPEARANCE]:
		"border-pink-300 text-pink-800 dark:border-pink-600 dark:text-pink-200",
	[IdentityCategory.PHYSICAL_EXPRESSION]:
		"border-blue-300 text-blue-800 dark:border-blue-600 dark:text-blue-200",
	[IdentityCategory.FAMILIAL_RELATIONS]:
		"border-indigo-300 text-indigo-800 dark:border-indigo-600 dark:text-indigo-200",
	[IdentityCategory.ROMANTIC_RELATION]:
		"border-red-300 text-red-800 dark:border-red-600 dark:text-red-200",
	[IdentityCategory.DOER_OF_THINGS]:
		"border-teal-300 text-teal-800 dark:border-teal-600 dark:text-teal-200",
};

/**
 * Helper function to get the display name for an identity category
 */
export const getIdentityCategoryDisplayName = (category: string): string => {
	// Handle null/undefined
	if (!category) return category;

	// Try exact match first
	if (IDENTITY_CATEGORY_DISPLAY_NAMES[category as IdentityCategory]) {
		return IDENTITY_CATEGORY_DISPLAY_NAMES[category as IdentityCategory];
	}

	// Try case-insensitive match
	const normalizedCategory = category.toLowerCase();
	for (const [key, displayName] of Object.entries(
		IDENTITY_CATEGORY_DISPLAY_NAMES,
	)) {
		if (key.toLowerCase() === normalizedCategory) {
			return displayName;
		}
	}

	// Fallback to original value
	return category;
};

/**
 * Helper function to get the short description for an identity category
 */
export const getIdentityCategoryDescription = (category: string): string => {
	if (!category) return "";

	// Try exact match first
	if (IDENTITY_CATEGORY_DESCRIPTIONS[category as IdentityCategory]) {
		return IDENTITY_CATEGORY_DESCRIPTIONS[category as IdentityCategory];
	}

	// Try case-insensitive match
	const normalizedCategory = category.toLowerCase();
	for (const [key, description] of Object.entries(
		IDENTITY_CATEGORY_DESCRIPTIONS,
	)) {
		if (key.toLowerCase() === normalizedCategory) {
			return description;
		}
	}

	return "";
};

/**
 * Helper function to get the color classes for an identity category (for badges)
 */
export const getIdentityCategoryColor = (category: string): string => {
	// Handle null/undefined
	if (!category)
		return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";

	// Try exact match first
	if (IDENTITY_CATEGORY_COLORS[category as IdentityCategory]) {
		return IDENTITY_CATEGORY_COLORS[category as IdentityCategory];
	}

	// Try case-insensitive match
	const normalizedCategory = category.toLowerCase();
	for (const [key, color] of Object.entries(IDENTITY_CATEGORY_COLORS)) {
		if (key.toLowerCase() === normalizedCategory) {
			return color;
		}
	}

	// Fallback to gray
	return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
};

/**
 * Helper function to get the light background color for an identity category (for cards)
 */
export const getIdentityCategoryLightColor = (category: string): string => {
	// Handle null/undefined
	if (!category) return "bg-gray-50 dark:bg-gray-950";

	// Try exact match first
	if (IDENTITY_CATEGORY_LIGHT_COLORS[category as IdentityCategory]) {
		return IDENTITY_CATEGORY_LIGHT_COLORS[category as IdentityCategory];
	}

	// Try case-insensitive match
	const normalizedCategory = category.toLowerCase();
	for (const [key, color] of Object.entries(IDENTITY_CATEGORY_LIGHT_COLORS)) {
		if (key.toLowerCase() === normalizedCategory) {
			return color;
		}
	}

	// Fallback to gray
	return "bg-gray-50 dark:bg-gray-950";
};

/**
 * Helper function to get the dark colors for borders, text, and icons
 */
export const getIdentityCategoryDarkColor = (category: string): string => {
	// Handle null/undefined
	if (!category)
		return "border-gray-300 text-gray-800 dark:border-gray-600 dark:text-gray-200";

	// Try exact match first
	if (IDENTITY_CATEGORY_DARK_COLORS[category as IdentityCategory]) {
		return IDENTITY_CATEGORY_DARK_COLORS[category as IdentityCategory];
	}

	// Try case-insensitive match
	const normalizedCategory = category.toLowerCase();
	for (const [key, color] of Object.entries(IDENTITY_CATEGORY_DARK_COLORS)) {
		if (key.toLowerCase() === normalizedCategory) {
			return color;
		}
	}

	// Fallback to gray
	return "border-gray-300 text-gray-800 dark:border-gray-600 dark:text-gray-200";
};

/**
 * Maps identity category values to their corresponding React icon components
 */
export const IDENTITY_CATEGORY_ICON_MAP: Record<
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

/**
 * Helper function to get the appropriate icon component for an identity category
 */
export const getIdentityCategoryIcon = (
	category: string,
): React.ComponentType<{ className?: string }> => {
	const normalizedCategory = category.toLowerCase();
	if (IDENTITY_CATEGORY_ICON_MAP[normalizedCategory]) {
		return IDENTITY_CATEGORY_ICON_MAP[normalizedCategory];
	}
	for (const [key, icon] of Object.entries(IDENTITY_CATEGORY_ICON_MAP)) {
		if (
			normalizedCategory.includes(key.split("_")[0]) ||
			key.split("_").some((part) => normalizedCategory.includes(part))
		) {
			return icon;
		}
	}
	return FaUser;
};
