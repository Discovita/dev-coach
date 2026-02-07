import { BadgeSelector, BadgeOption } from "./BadgeSelector";
import { Build, BUILD_DISPLAY_NAMES, BUILDS_BY_GENDER } from "@/enums/appearance/build";
import { Gender } from "@/enums/appearance/gender";

interface BuildSelectorProps {
  value: Build | null | undefined;
  onChange: (value: Build) => void;
  /** Selected gender - determines which build options are shown */
  gender: Gender | null | undefined;
}

/**
 * BuildSelector Component
 * ----------------------
 * Badge selector for build/body type preference.
 * Filters available options based on the user's selected gender.
 * 
 * - Male: slim, athletic, average, muscular, stocky, large
 * - Female: petite, slim, athletic, average, curvy, full_figured
 * - Neutral: slim, athletic, average, stocky, large, heavyset
 */
export function BuildSelector({ value, onChange, gender }: BuildSelectorProps) {
  // Get gender-specific build options, default to neutral if no gender selected
  const availableBuilds = gender 
    ? BUILDS_BY_GENDER[gender] 
    : BUILDS_BY_GENDER[Gender.PERSON];

  const options: BadgeOption<Build>[] = availableBuilds.map((build) => ({
    value: build,
    label: BUILD_DISPLAY_NAMES[build],
  }));

  // Check if current value is valid for the selected gender
  const isValueValid = value && availableBuilds.includes(value);

  return (
    <BadgeSelector<Build>
      label="Build"
      options={options}
      value={isValueValid ? value : null}
      onChange={onChange}
    />
  );
}
