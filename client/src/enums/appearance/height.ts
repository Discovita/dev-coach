/**
 * Represents height visualization options for image generation.
 * Used in the User model to store appearance preferences.
 */
export enum Height {
  SHORT = "short",
  BELOW_AVERAGE = "below_average",
  AVERAGE = "average",
  ABOVE_AVERAGE = "above_average",
  TALL = "tall",
}

/**
 * Maps height values to their human-readable display names
 */
export const HEIGHT_DISPLAY_NAMES: Record<Height, string> = {
  [Height.SHORT]: "Short",
  [Height.BELOW_AVERAGE]: "Below Average",
  [Height.AVERAGE]: "Average",
  [Height.ABOVE_AVERAGE]: "Above Average",
  [Height.TALL]: "Tall",
};
