/**
 * Represents build/body type visualization options for image generation.
 * Used in the User model to store appearance preferences.
 */
export enum Build {
  SLIM = "slim",
  ATHLETIC = "athletic",
  AVERAGE = "average",
  STOCKY = "stocky",
  LARGE = "large",
}

/**
 * Maps build values to their human-readable display names
 */
export const BUILD_DISPLAY_NAMES: Record<Build, string> = {
  [Build.SLIM]: "Slim",
  [Build.ATHLETIC]: "Athletic",
  [Build.AVERAGE]: "Average",
  [Build.STOCKY]: "Stocky",
  [Build.LARGE]: "Large",
};
