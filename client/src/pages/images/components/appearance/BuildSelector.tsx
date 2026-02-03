import { BadgeSelector, BadgeOption } from "./BadgeSelector";
import { Build, BUILD_DISPLAY_NAMES } from "@/enums/appearance/build";

interface BuildSelectorProps {
  value: Build | null | undefined;
  onChange: (value: Build) => void;
}

/**
 * BuildSelector Component
 * ----------------------
 * Badge selector for build/body type preference.
 */
export function BuildSelector({ value, onChange }: BuildSelectorProps) {
  const options: BadgeOption<Build>[] = Object.values(Build).map((build) => ({
    value: build,
    label: BUILD_DISPLAY_NAMES[build],
  }));

  return (
    <BadgeSelector<Build>
      label="Build"
      options={options}
      value={value || null}
      onChange={onChange}
    />
  );
}
