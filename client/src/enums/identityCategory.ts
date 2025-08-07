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
};

/**
 * Maps identity category values to their color classes
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
 * Helper function to get the color classes for an identity category
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
