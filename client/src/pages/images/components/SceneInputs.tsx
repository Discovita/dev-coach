import { useState, useEffect, useMemo } from "react";
import { SceneInputs as SceneInputsType } from "@/types/sceneInputs";
import { ClothingInput } from "./scene/ClothingInput";
import { MoodInput } from "./scene/MoodInput";
import { SettingInput } from "./scene/SettingInput";
import { Button } from "@/components/ui/button";
import { Info, Save, Check, AlertCircle } from "lucide-react";

interface SceneInputsProps {
  /** Current local values (for editing) */
  values: SceneInputsType;
  /** Values currently saved on the identity */
  savedValues: SceneInputsType;
  /** Callback when values change */
  onChange: (values: SceneInputsType) => void;
  /** Callback to save changes to identity */
  onSave: () => Promise<void>;
  /** Whether a save operation is in progress */
  isSaving?: boolean;
  /** Whether inputs should be disabled */
  disabled?: boolean;
}

/**
 * List of all scene fields.
 */
const SCENE_FIELDS: (keyof SceneInputsType)[] = ["clothing", "mood", "setting"];

/**
 * Human-readable labels for each scene field.
 */
const FIELD_LABELS: Record<keyof SceneInputsType, string> = {
  clothing: "Clothing",
  mood: "Mood",
  setting: "Setting",
};

/**
 * Normalizes a value to a string for comparison (handles null/undefined/empty).
 */
function normalizeValue(value: string | null | undefined): string {
  return (value || "").trim();
}

/**
 * Checks if two scene input objects are equal (for dirty state detection).
 */
function sceneInputsEquals(
  a: SceneInputsType,
  b: SceneInputsType
): boolean {
  return SCENE_FIELDS.every(
    (field) => normalizeValue(a[field]) === normalizeValue(b[field])
  );
}

/**
 * Gets the list of empty field labels.
 */
function getEmptyFields(values: SceneInputsType): string[] {
  return SCENE_FIELDS.filter(
    (field) => !normalizeValue(values[field])
  ).map((f) => FIELD_LABELS[f]);
}

/**
 * SceneInputs Component
 * ---------------------
 * Container component for scene-specific inputs (clothing, mood, setting).
 * These fields are saved to the Identity model and vary per identity.
 * 
 * Features:
 * - Local state for unsaved changes
 * - Explicit "Save Scene Details" button
 * - Validation showing which fields are empty (soft warning)
 * - Dirty state tracking
 * - Success feedback after saving
 * 
 * Displays three text inputs:
 * - What are you wearing? (clothing)
 * - How do you feel? (mood)
 * - What is the setting? (setting)
 */
export function SceneInputs({
  values,
  savedValues,
  onChange,
  onSave,
  isSaving = false,
  disabled = false,
}: SceneInputsProps) {
  // Track if save was recently successful (for showing success indicator)
  const [showSaveSuccess, setShowSaveSuccess] = useState(false);

  // Calculate derived state
  const isDirty = useMemo(
    () => !sceneInputsEquals(values, savedValues),
    [values, savedValues]
  );
  const emptyFields = useMemo(() => getEmptyFields(values), [values]);
  const hasAllFields = emptyFields.length === 0;

  // Clear success indicator when values change
  useEffect(() => {
    if (isDirty) {
      setShowSaveSuccess(false);
    }
  }, [isDirty]);

  const handleChange = <K extends keyof SceneInputsType>(
    field: K,
    value: SceneInputsType[K]
  ) => {
    onChange({
      ...values,
      [field]: value,
    });
  };

  // Handle save button click
  const handleSave = async () => {
    try {
      await onSave();
      setShowSaveSuccess(true);
      // Hide success indicator after 3 seconds
      setTimeout(() => setShowSaveSuccess(false), 3000);
    } catch {
      // Error handling is done in the parent component
    }
  };

  return (
    <div className="space-y-6 p-4 border rounded-lg bg-neutral-50 dark:bg-neutral-900/50">
      {/* Header */}
      <div className="flex items-start gap-2">
        <h2 className="text-lg font-semibold">
          Scene Details for this Identity
        </h2>
        <Info className="size-4 text-neutral-500 mt-0.5" />
      </div>
      <p className="text-xs text-neutral-500 -mt-4">
        These are saved to the identity
      </p>

      {/* Validation Warning */}
      {!hasAllFields && (
        <div className="flex items-start gap-2 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
          <AlertCircle className="size-4 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-amber-800 dark:text-amber-200">
            <p className="font-medium">
              Fill in all scene details for best results
            </p>
            <p className="text-xs mt-1 text-amber-700 dark:text-amber-300">
              Missing: {emptyFields.join(", ")}
            </p>
          </div>
        </div>
      )}

      {/* Inputs */}
      <div className="space-y-4">
        <ClothingInput
          value={values.clothing}
          onChange={(value) => handleChange("clothing", value)}
          disabled={disabled}
        />

        <MoodInput
          value={values.mood}
          onChange={(value) => handleChange("mood", value)}
          disabled={disabled}
        />

        <SettingInput
          value={values.setting}
          onChange={(value) => handleChange("setting", value)}
          disabled={disabled}
        />
      </div>

      {/* Footer with status and save button */}
      <div className="flex items-center justify-between pt-4 border-t border-neutral-200 dark:border-neutral-700">
        {/* Status indicator */}
        <div className="flex items-center gap-2">
          {isDirty ? (
            <span className="text-sm text-amber-600 dark:text-amber-400">
              Unsaved changes
            </span>
          ) : (
            <span className="text-sm text-green-600 dark:text-green-400 flex items-center gap-1">
              <Check className="size-4" />
              All changes saved
            </span>
          )}
        </div>

        {/* Save button */}
        <div className="flex items-center gap-2">
          {showSaveSuccess && (
            <span className="text-sm text-green-600 dark:text-green-400 flex items-center gap-1">
              <Check className="size-4" />
              Saved!
            </span>
          )}
          <Button
            type="button"
            variant="default"
            onClick={handleSave}
            disabled={!isDirty || isSaving || disabled}
            className="gap-2"
          >
            {isSaving ? (
              <>
                <Save className="size-4 animate-pulse" />
                Saving...
              </>
            ) : (
              <>
                <Save className="size-4" />
                Save Scene Details
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
