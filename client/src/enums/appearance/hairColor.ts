/**
 * Represents hair color options for image generation.
 * Used in the User model to store appearance preferences.
 */
export enum HairColor {
  BLACK = "black",
  BROWN = "brown",
  BLONDE = "blonde",
  RED = "red",
  AUBURN = "auburn",
  GRAY = "gray",
  WHITE = "white",
  BALD = "bald",
}

/**
 * Maps hair color values to their human-readable display names
 */
export const HAIR_COLOR_DISPLAY_NAMES: Record<HairColor, string> = {
  [HairColor.BLACK]: "Black",
  [HairColor.BROWN]: "Brown",
  [HairColor.BLONDE]: "Blonde",
  [HairColor.RED]: "Red",
  [HairColor.AUBURN]: "Auburn",
  [HairColor.GRAY]: "Gray",
  [HairColor.WHITE]: "White",
  [HairColor.BALD]: "Bald",
};
