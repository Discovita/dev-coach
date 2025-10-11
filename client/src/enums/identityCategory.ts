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
  REVIEW = "review",
}

/**
 * Maps identity category values to their human-readable display names
 */
export const IDENTITY_CATEGORY_DISPLAY_NAMES: Record<IdentityCategory, string> = {
  [IdentityCategory.PASSIONS_AND_TALENTS]: "Passions and Talents",
  [IdentityCategory.MAKER_OF_MONEY]: "Maker of Money",
  [IdentityCategory.KEEPER_OF_MONEY]: "Keeper of Money",
  [IdentityCategory.SPIRITUAL]: "Spiritual",
  [IdentityCategory.PERSONAL_APPEARANCE]: "Personal Appearance",
  [IdentityCategory.PHYSICAL_EXPRESSION]: "Physical Expression",
  [IdentityCategory.FAMILIAL_RELATIONS]: "Familial Relations",
  [IdentityCategory.ROMANTIC_RELATION]: "Romantic Relation",
  [IdentityCategory.DOER_OF_THINGS]: "Doer of Things",
  [IdentityCategory.REVIEW]: "Review",
};

/**
 * Maps identity category values to their color classes for badges
 */
export const IDENTITY_CATEGORY_COLORS: Record<IdentityCategory, string> = {
  [IdentityCategory.PASSIONS_AND_TALENTS]: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  [IdentityCategory.MAKER_OF_MONEY]: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  [IdentityCategory.KEEPER_OF_MONEY]: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
  [IdentityCategory.SPIRITUAL]: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  [IdentityCategory.PERSONAL_APPEARANCE]: "bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200",
  [IdentityCategory.PHYSICAL_EXPRESSION]: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  [IdentityCategory.FAMILIAL_RELATIONS]: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200",
  [IdentityCategory.ROMANTIC_RELATION]: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  [IdentityCategory.DOER_OF_THINGS]: "bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200",
  [IdentityCategory.REVIEW]: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
  };

/**
 * Maps identity category values to their light background colors for cards
 */
export const IDENTITY_CATEGORY_LIGHT_COLORS: Record<IdentityCategory, string> = {
  [IdentityCategory.PASSIONS_AND_TALENTS]: "bg-orange-50 dark:bg-orange-950",
  [IdentityCategory.MAKER_OF_MONEY]: "bg-green-50 dark:bg-green-950",
  [IdentityCategory.KEEPER_OF_MONEY]: "bg-emerald-50 dark:bg-emerald-950",
  [IdentityCategory.SPIRITUAL]: "bg-purple-50 dark:bg-purple-950",
  [IdentityCategory.PERSONAL_APPEARANCE]: "bg-pink-50 dark:bg-pink-950",
  [IdentityCategory.PHYSICAL_EXPRESSION]: "bg-blue-50 dark:bg-blue-950",
  [IdentityCategory.FAMILIAL_RELATIONS]: "bg-indigo-50 dark:bg-indigo-950",
  [IdentityCategory.ROMANTIC_RELATION]: "bg-red-50 dark:bg-red-950",
  [IdentityCategory.DOER_OF_THINGS]: "bg-teal-50 dark:bg-teal-950",
  [IdentityCategory.REVIEW]: "bg-gray-50 dark:bg-gray-950",
};

/**
 * Maps identity category values to their dark colors for borders, text, and icons
 */
export const IDENTITY_CATEGORY_DARK_COLORS: Record<IdentityCategory, string> = {
  [IdentityCategory.PASSIONS_AND_TALENTS]: "border-orange-300 text-orange-800 dark:border-orange-600 dark:text-orange-200",
  [IdentityCategory.MAKER_OF_MONEY]: "border-green-300 text-green-800 dark:border-green-600 dark:text-green-200",
  [IdentityCategory.KEEPER_OF_MONEY]: "border-emerald-300 text-emerald-800 dark:border-emerald-600 dark:text-emerald-200",
  [IdentityCategory.SPIRITUAL]: "border-purple-300 text-purple-800 dark:border-purple-600 dark:text-purple-200",
  [IdentityCategory.PERSONAL_APPEARANCE]: "border-pink-300 text-pink-800 dark:border-pink-600 dark:text-pink-200",
  [IdentityCategory.PHYSICAL_EXPRESSION]: "border-blue-300 text-blue-800 dark:border-blue-600 dark:text-blue-200",
  [IdentityCategory.FAMILIAL_RELATIONS]: "border-indigo-300 text-indigo-800 dark:border-indigo-600 dark:text-indigo-200",
  [IdentityCategory.ROMANTIC_RELATION]: "border-red-300 text-red-800 dark:border-red-600 dark:text-red-200",
  [IdentityCategory.DOER_OF_THINGS]: "border-teal-300 text-teal-800 dark:border-teal-600 dark:text-teal-200",
  [IdentityCategory.REVIEW]: "border-gray-300 text-gray-800 dark:border-gray-600 dark:text-gray-200",
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
  for (const [key, displayName] of Object.entries(IDENTITY_CATEGORY_DISPLAY_NAMES)) {
    if (key.toLowerCase() === normalizedCategory) {
      return displayName;
    }
  }
  
  // Fallback to original value
  return category;
};

/**
 * Helper function to get the color classes for an identity category (for badges)
 */
export const getIdentityCategoryColor = (category: string): string => {
  // Handle null/undefined
  if (!category) return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
  
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
  if (!category) return "border-gray-300 text-gray-800 dark:border-gray-600 dark:text-gray-200";
  
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
