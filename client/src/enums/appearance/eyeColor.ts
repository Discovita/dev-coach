/**
 * Represents eye color options for image generation.
 * Used in the User model to store appearance preferences.
 */
export enum EyeColor {
  BROWN = "brown",
  BLUE = "blue",
  GREEN = "green",
  HAZEL = "hazel",
  GRAY = "gray",
  AMBER = "amber",
}

/**
 * Maps eye color values to their human-readable display names
 */
export const EYE_COLOR_DISPLAY_NAMES: Record<EyeColor, string> = {
  [EyeColor.BROWN]: "Brown",
  [EyeColor.BLUE]: "Blue",
  [EyeColor.GREEN]: "Green",
  [EyeColor.HAZEL]: "Hazel",
  [EyeColor.GRAY]: "Gray",
  [EyeColor.AMBER]: "Amber",
};
