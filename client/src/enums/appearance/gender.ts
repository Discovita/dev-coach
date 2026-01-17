/**
 * Represents gender visualization options for image generation.
 * Used in the User model to store appearance preferences.
 */
export enum Gender {
  MAN = "man",
  WOMAN = "woman",
  PERSON = "person", // Gender neutral
}

/**
 * Maps gender values to their human-readable display names
 */
export const GENDER_DISPLAY_NAMES: Record<Gender, string> = {
  [Gender.MAN]: "Man",
  [Gender.WOMAN]: "Woman",
  [Gender.PERSON]: "Person",
};
