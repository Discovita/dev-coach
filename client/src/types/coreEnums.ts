/**
 * Enum option structure returned from the backend API.
 * Each enum option has a value and label for display.
 */
export interface EnumOption {
  value: string;
  label: string;
}

/**
 * Appearance enums structure returned from the backend API.
 * Contains all appearance-related enum options for user visualization preferences.
 */
export interface AppearanceEnums {
  genders: EnumOption[];
  skin_tones: EnumOption[];
  hair_colors: EnumOption[];
  eye_colors: EnumOption[];
  heights: EnumOption[];
  builds: EnumOption[];
  age_ranges: EnumOption[];
}

/**
 * Core enums response structure from the backend API.
 * Contains all enum options used throughout the application.
 */
export interface CoreEnumsResponse {
  coaching_phases: EnumOption[];
  allowed_actions: EnumOption[];
  context_keys: EnumOption[];
  prompt_types: EnumOption[];
  appearance: AppearanceEnums;
}
