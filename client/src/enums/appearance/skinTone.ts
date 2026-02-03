/**
 * Represents skin tone options following Apple emoji convention.
 * Used in the User model to store appearance preferences for image generation.
 */
export enum SkinTone {
  LIGHT = "light",
  MEDIUM_LIGHT = "medium_light",
  MEDIUM = "medium",
  MEDIUM_DARK = "medium_dark",
  DARK = "dark",
}

/**
 * Maps skin tone values to their human-readable display names
 */
export const SKIN_TONE_DISPLAY_NAMES: Record<SkinTone, string> = {
  [SkinTone.LIGHT]: "Light",
  [SkinTone.MEDIUM_LIGHT]: "Medium-Light",
  [SkinTone.MEDIUM]: "Medium",
  [SkinTone.MEDIUM_DARK]: "Medium-Dark",
  [SkinTone.DARK]: "Dark",
};

/**
 * Maps skin tone values to their color hex codes for visual representation
 */
export const SKIN_TONE_COLORS: Record<SkinTone, string> = {
  [SkinTone.LIGHT]: "#ffecd2",
  [SkinTone.MEDIUM_LIGHT]: "#e8c4a2",
  [SkinTone.MEDIUM]: "#c49a6c",
  [SkinTone.MEDIUM_DARK]: "#8d5524",
  [SkinTone.DARK]: "#5c3836",
};
