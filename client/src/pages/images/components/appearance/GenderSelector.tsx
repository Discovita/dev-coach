import { BadgeSelector, BadgeOption } from "./BadgeSelector";
import { Gender, GENDER_DISPLAY_NAMES } from "@/enums/appearance/gender";

interface GenderSelectorProps {
  value: Gender | null | undefined;
  onChange: (value: Gender) => void;
}

/**
 * GenderSelector Component
 * -----------------------
 * Badge selector for gender preference (man, woman, person).
 */
export function GenderSelector({ value, onChange }: GenderSelectorProps) {
  const options: BadgeOption<Gender>[] = Object.values(Gender).map((gender) => ({
    value: gender,
    label: GENDER_DISPLAY_NAMES[gender],
  }));

  return (
    <BadgeSelector<Gender>
      label="Gender"
      options={options}
      value={value || null}
      onChange={onChange}
    />
  );
}
