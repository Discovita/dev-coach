/**
 * Appearance selector components for user visualization preferences.
 * Used on the Account page for configuring image generation settings.
 */

export { AppearanceSelector } from "./AppearanceSelector";
export {
  AppearanceFields,
  APPEARANCE_FIELDS,
  FIELD_LABELS,
  countFilledFields,
  getMissingFields,
  appearanceEquals,
  applyAppearanceChange,
} from "./AppearanceFields";
export { BadgeSelector } from "./BadgeSelector";
export type { BadgeOption } from "./BadgeSelector";
export { GenderSelector } from "./GenderSelector";
export { SkinToneSelector } from "./SkinToneSelector";
export { HairColorSelector } from "./HairColorSelector";
export { EyeColorSelector } from "./EyeColorSelector";
export { HeightSelector } from "./HeightSelector";
export { BuildSelector } from "./BuildSelector";
export { AgeRangeSelector } from "./AgeRangeSelector";
