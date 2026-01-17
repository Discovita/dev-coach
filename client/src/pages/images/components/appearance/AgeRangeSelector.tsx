import { BadgeSelector, BadgeOption } from "./BadgeSelector";
import { AgeRange, AGE_RANGE_DISPLAY_NAMES } from "@/enums/appearance/ageRange";

interface AgeRangeSelectorProps {
  value: AgeRange | null | undefined;
  onChange: (value: AgeRange) => void;
}

/**
 * AgeRangeSelector Component
 * ---------------------------
 * Badge selector for age range preference.
 */
export function AgeRangeSelector({ value, onChange }: AgeRangeSelectorProps) {
  const options: BadgeOption<AgeRange>[] = Object.values(AgeRange).map((ageRange) => ({
    value: ageRange,
    label: AGE_RANGE_DISPLAY_NAMES[ageRange],
  }));

  return (
    <BadgeSelector<AgeRange>
      label="Age"
      options={options}
      value={value || null}
      onChange={onChange}
    />
  );
}
