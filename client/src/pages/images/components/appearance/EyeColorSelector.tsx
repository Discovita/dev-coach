import { BadgeSelector, BadgeOption } from "./BadgeSelector";
import { EyeColor, EYE_COLOR_DISPLAY_NAMES } from "@/enums/appearance/eyeColor";

interface EyeColorSelectorProps {
  value: EyeColor | null | undefined;
  onChange: (value: EyeColor) => void;
}

/**
 * EyeColorSelector Component
 * --------------------------
 * Badge selector for eye color preference.
 */
export function EyeColorSelector({ value, onChange }: EyeColorSelectorProps) {
  const options: BadgeOption<EyeColor>[] = Object.values(EyeColor).map((color) => ({
    value: color,
    label: EYE_COLOR_DISPLAY_NAMES[color],
  }));

  return (
    <BadgeSelector<EyeColor>
      label="Eye Color"
      options={options}
      value={value || null}
      onChange={onChange}
    />
  );
}
