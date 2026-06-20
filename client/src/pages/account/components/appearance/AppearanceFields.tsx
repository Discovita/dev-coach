import type { UserAppearance } from "@/types/userAppearance";
import { GenderSelector } from "./GenderSelector";
import { SkinToneSelector } from "./SkinToneSelector";
import { HairColorSelector } from "./HairColorSelector";
import { EyeColorSelector } from "./EyeColorSelector";
import { HeightSelector } from "./HeightSelector";
import { BuildSelector } from "./BuildSelector";
import { AgeRangeSelector } from "./AgeRangeSelector";
import { Gender } from "@/enums/appearance/gender";
import { BUILDS_BY_GENDER } from "@/enums/appearance/build";

/**
 * List of all appearance fields that are required for image generation.
 * Used for validation and progress tracking.
 */
export const APPEARANCE_FIELDS: (keyof UserAppearance)[] = [
  "gender",
  "skin_tone",
  "hair_color",
  "eye_color",
  "height",
  "build",
  "age_range",
];

/**
 * Human-readable labels for each appearance field.
 * Used in validation messages.
 */
export const FIELD_LABELS: Record<keyof UserAppearance, string> = {
  gender: "Gender",
  skin_tone: "Skin Tone",
  hair_color: "Hair Color",
  eye_color: "Eye Color",
  height: "Height",
  build: "Build",
  age_range: "Age",
};

/**
 * Checks if an appearance field has a valid value (not null/undefined).
 */
function hasValue(value: unknown): boolean {
  return value !== null && value !== undefined;
}

/**
 * Counts how many appearance fields have values.
 */
export function countFilledFields(appearance: UserAppearance | null): number {
  if (!appearance) return 0;
  return APPEARANCE_FIELDS.filter((field) => hasValue(appearance[field])).length;
}

/**
 * Gets the list of missing (unfilled) field labels.
 */
export function getMissingFields(appearance: UserAppearance | null): string[] {
  if (!appearance) return APPEARANCE_FIELDS.map((f) => FIELD_LABELS[f]);
  return APPEARANCE_FIELDS.filter((field) => !hasValue(appearance[field])).map(
    (f) => FIELD_LABELS[f]
  );
}

/**
 * Checks if two appearance objects are equal (for dirty state detection).
 */
export function appearanceEquals(
  a: UserAppearance | null,
  b: UserAppearance | null
): boolean {
  if (a === b) return true;
  if (!a || !b) return false;
  return APPEARANCE_FIELDS.every((field) => a[field] === b[field]);
}

/**
 * Applies a single field change to an appearance object, returning a new object.
 * When gender changes, clears build if it's no longer valid for the new gender.
 */
export function applyAppearanceChange<K extends keyof UserAppearance>(
  prev: UserAppearance,
  field: K,
  value: UserAppearance[K]
): UserAppearance {
  const updated: UserAppearance = { ...prev, [field]: value };

  if (field === "gender" && prev.build) {
    const newGender = value as Gender;
    const validBuilds =
      BUILDS_BY_GENDER[newGender] || BUILDS_BY_GENDER[Gender.PERSON];
    if (!validBuilds.includes(prev.build)) {
      updated.build = undefined;
    }
  }

  return updated;
}

interface AppearanceFieldsProps {
  /** Current appearance values to display */
  value: UserAppearance;
  /** Called with the full next appearance object whenever a field changes */
  onChange: (next: UserAppearance) => void;
}

/**
 * AppearanceFields Component
 * --------------------------
 * The bare set of appearance badge selectors (gender, skin tone, hair color,
 * eye color, height, build, age range) with no surrounding card, heading, or
 * save chrome. Fully controlled via `value` / `onChange`.
 *
 * Encapsulates the gender→build clearing rule so callers never duplicate it.
 *
 * Used in: AppearanceSelector (account page) and the onboarding flow.
 */
export function AppearanceFields({ value, onChange }: AppearanceFieldsProps) {
  const handleChange = <K extends keyof UserAppearance>(
    field: K,
    fieldValue: UserAppearance[K]
  ) => {
    onChange(applyAppearanceChange(value, field, fieldValue));
  };

  return (
    <div className="space-y-6">
      <GenderSelector
        value={value.gender}
        onChange={(v) => handleChange("gender", v)}
      />

      <SkinToneSelector
        value={value.skin_tone}
        onChange={(v) => handleChange("skin_tone", v)}
      />

      <HairColorSelector
        value={value.hair_color}
        onChange={(v) => handleChange("hair_color", v)}
      />

      <EyeColorSelector
        value={value.eye_color}
        onChange={(v) => handleChange("eye_color", v)}
      />

      <HeightSelector
        value={value.height}
        onChange={(v) => handleChange("height", v)}
      />

      <BuildSelector
        value={value.build}
        onChange={(v) => handleChange("build", v)}
        gender={value.gender}
      />

      <AgeRangeSelector
        value={value.age_range}
        onChange={(v) => handleChange("age_range", v)}
      />
    </div>
  );
}
