import { UserAppearance } from "@/types/userAppearance";
import { GenderSelector } from "./GenderSelector";
import { SkinToneSelector } from "./SkinToneSelector";
import { HairColorSelector } from "./HairColorSelector";
import { EyeColorSelector } from "./EyeColorSelector";
import { HeightSelector } from "./HeightSelector";
import { BuildSelector } from "./BuildSelector";
import { AgeRangeSelector } from "./AgeRangeSelector";
import { Info } from "lucide-react";

interface AppearanceSelectorProps {
  appearance: UserAppearance | null;
  onAppearanceChange: (appearance: UserAppearance) => void;
}

/**
 * AppearanceSelector Component
 * ----------------------------
 * Container component for all user appearance selectors.
 * Displays badge selectors for gender, skin tone, hair color, eye color,
 * height, build, and age range preferences.
 * 
 * These settings are saved to the User model and apply to all identity image generations.
 */
export function AppearanceSelector({
  appearance,
  onAppearanceChange,
}: AppearanceSelectorProps) {
  const handleChange = <K extends keyof UserAppearance>(
    field: K,
    value: UserAppearance[K]
  ) => {
    onAppearanceChange({
      ...appearance,
      [field]: value,
    } as UserAppearance);
  };

  return (
    <div className="space-y-6 p-4 border rounded-lg bg-neutral-50 dark:bg-neutral-900/50">
      <div className="flex items-start gap-2">
        <h2 className="text-lg font-semibold">
          How would you like to visualize yourself?
        </h2>
        <Info className="size-4 text-neutral-500 mt-0.5" />
      </div>
      <p className="text-xs text-neutral-500 -mt-4">
        These settings are saved to your user profile
      </p>

      <div className="space-y-6">
        <GenderSelector
          value={appearance?.gender}
          onChange={(value) => handleChange("gender", value)}
        />

        <SkinToneSelector
          value={appearance?.skin_tone}
          onChange={(value) => handleChange("skin_tone", value)}
        />

        <HairColorSelector
          value={appearance?.hair_color}
          onChange={(value) => handleChange("hair_color", value)}
        />

        <EyeColorSelector
          value={appearance?.eye_color}
          onChange={(value) => handleChange("eye_color", value)}
        />

        <HeightSelector
          value={appearance?.height}
          onChange={(value) => handleChange("height", value)}
        />

        <BuildSelector
          value={appearance?.build}
          onChange={(value) => handleChange("build", value)}
        />

        <AgeRangeSelector
          value={appearance?.age_range}
          onChange={(value) => handleChange("age_range", value)}
        />
      </div>
    </div>
  );
}
