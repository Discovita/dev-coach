import { Gender } from "./gender";

/**
 * Represents build/body type visualization options for image generation.
 * Used in the User model to store appearance preferences.
 * 
 * Contains all possible build values. The frontend filters which options
 * to display based on the user's selected gender.
 */
export enum Build {
  // Shared across genders
  SLIM = "slim",
  ATHLETIC = "athletic",
  AVERAGE = "average",
  STOCKY = "stocky",
  LARGE = "large",
  
  // Male-specific
  MUSCULAR = "muscular",
  
  // Female-specific
  PETITE = "petite",
  CURVY = "curvy",
  FULL_FIGURED = "full_figured",
  
  // Neutral-specific
  HEAVYSET = "heavyset",
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
  [Build.MUSCULAR]: "Muscular",
  [Build.PETITE]: "Petite",
  [Build.CURVY]: "Curvy",
  [Build.FULL_FIGURED]: "Full-Figured",
  [Build.HEAVYSET]: "Heavyset",
};

/**
 * Gender-specific build options, ordered from smallest to largest.
 * Used by BuildSelector to filter options based on selected gender.
 */
export const BUILDS_BY_GENDER: Record<Gender, Build[]> = {
  [Gender.MAN]: [
    Build.SLIM,
    Build.ATHLETIC,
    Build.AVERAGE,
    Build.MUSCULAR,
    Build.STOCKY,
    Build.LARGE,
  ],
  [Gender.WOMAN]: [
    Build.PETITE,
    Build.SLIM,
    Build.ATHLETIC,
    Build.AVERAGE,
    Build.CURVY,
    Build.FULL_FIGURED,
  ],
  [Gender.PERSON]: [
    Build.SLIM,
    Build.ATHLETIC,
    Build.AVERAGE,
    Build.STOCKY,
    Build.LARGE,
    Build.HEAVYSET,
  ],
};
