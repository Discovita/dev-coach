import { SceneInputs as SceneInputsType } from "@/types/sceneInputs";
import { ClothingInput } from "./scene/ClothingInput";
import { MoodInput } from "./scene/MoodInput";
import { SettingInput } from "./scene/SettingInput";
import { Info } from "lucide-react";

interface SceneInputsProps {
  values: SceneInputsType;
  onChange: (values: SceneInputsType) => void;
}

/**
 * SceneInputs Component
 * ---------------------
 * Container component for scene-specific inputs (clothing, mood, setting).
 * These fields are saved to the Identity model and vary per identity.
 * 
 * Displays three text inputs:
 * - What are you wearing? (clothing)
 * - How do you feel? (mood)
 * - What is the setting? (setting)
 */
export function SceneInputs({ values, onChange }: SceneInputsProps) {
  const handleChange = <K extends keyof SceneInputsType>(
    field: K,
    value: SceneInputsType[K]
  ) => {
    onChange({
      ...values,
      [field]: value,
    });
  };

  return (
    <div className="space-y-6 p-4 border rounded-lg bg-neutral-50 dark:bg-neutral-900/50">
      <div className="flex items-start gap-2">
        <h2 className="text-lg font-semibold">
          Scene Details for this Identity
        </h2>
        <Info className="size-4 text-neutral-500 mt-0.5" />
      </div>
      <p className="text-xs text-neutral-500 -mt-4">
        These are saved to the identity
      </p>

      <div className="space-y-4">
        <ClothingInput
          value={values.clothing}
          onChange={(value) => handleChange("clothing", value)}
        />

        <MoodInput
          value={values.mood}
          onChange={(value) => handleChange("mood", value)}
        />

        <SettingInput
          value={values.setting}
          onChange={(value) => handleChange("setting", value)}
        />
      </div>
    </div>
  );
}
