import { BadgeSelector, BadgeOption } from "./BadgeSelector";
import { Height, HEIGHT_DISPLAY_NAMES } from "@/enums/appearance/height";

interface HeightSelectorProps {
  value: Height | null | undefined;
  onChange: (value: Height) => void;
}

/**
 * HeightSelector Component
 * ------------------------
 * Badge selector for height preference.
 */
export function HeightSelector({ value, onChange }: HeightSelectorProps) {
  const options: BadgeOption<Height>[] = Object.values(Height).map((height) => ({
    value: height,
    label: HEIGHT_DISPLAY_NAMES[height],
  }));

  return (
    <BadgeSelector<Height>
      label="Height"
      options={options}
      value={value || null}
      onChange={onChange}
    />
  );
}
