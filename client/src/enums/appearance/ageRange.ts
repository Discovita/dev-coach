/**
 * Represents age range visualization options for image generation.
 * Used in the User model to store appearance preferences.
 */
export enum AgeRange {
  TWENTIES = "twenties",
  THIRTIES = "thirties",
  FORTIES = "forties",
  FIFTIES = "fifties",
  SIXTY_PLUS = "sixty_plus",
}

/**
 * Maps age range values to their human-readable display names
 */
export const AGE_RANGE_DISPLAY_NAMES: Record<AgeRange, string> = {
  [AgeRange.TWENTIES]: "Young Adult (20s)",
  [AgeRange.THIRTIES]: "In Their 30s",
  [AgeRange.FORTIES]: "In Their 40s",
  [AgeRange.FIFTIES]: "Middle-Aged (50s)",
  [AgeRange.SIXTY_PLUS]: "Mature (60+)",
};
