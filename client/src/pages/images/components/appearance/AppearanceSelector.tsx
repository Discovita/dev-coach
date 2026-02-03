import { useState, useEffect, useMemo } from "react";
import { UserAppearance } from "@/types/userAppearance";
import { GenderSelector } from "./GenderSelector";
import { SkinToneSelector } from "./SkinToneSelector";
import { HairColorSelector } from "./HairColorSelector";
import { EyeColorSelector } from "./EyeColorSelector";
import { HeightSelector } from "./HeightSelector";
import { BuildSelector } from "./BuildSelector";
import { AgeRangeSelector } from "./AgeRangeSelector";
import { Button } from "@/components/ui/button";
import { Info, Save, Check, AlertCircle } from "lucide-react";

/**
 * List of all appearance fields that are required for image generation.
 * Used for validation and progress tracking.
 */
const APPEARANCE_FIELDS: (keyof UserAppearance)[] = [
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
const FIELD_LABELS: Record<keyof UserAppearance, string> = {
  gender: "Gender",
  skin_tone: "Skin Tone",
  hair_color: "Hair Color",
  eye_color: "Eye Color",
  height: "Height",
  build: "Build",
  age_range: "Age",
};

interface AppearanceSelectorProps {
  /** Current saved appearance from the user profile */
  appearance: UserAppearance | null;
  /** Callback to save appearance changes */
  onSave: (appearance: UserAppearance) => Promise<void>;
  /** Whether a save operation is in progress */
  isSaving?: boolean;
}

/**
 * Checks if an appearance field has a valid value (not null/undefined).
 */
function hasValue(value: unknown): boolean {
  return value !== null && value !== undefined;
}

/**
 * Counts how many appearance fields have values.
 */
function countFilledFields(appearance: UserAppearance | null): number {
  if (!appearance) return 0;
  return APPEARANCE_FIELDS.filter((field) => hasValue(appearance[field])).length;
}

/**
 * Gets the list of missing (unfilled) field labels.
 */
function getMissingFields(appearance: UserAppearance | null): string[] {
  if (!appearance) return APPEARANCE_FIELDS.map((f) => FIELD_LABELS[f]);
  return APPEARANCE_FIELDS.filter((field) => !hasValue(appearance[field])).map(
    (f) => FIELD_LABELS[f]
  );
}

/**
 * Checks if two appearance objects are equal (for dirty state detection).
 */
function appearanceEquals(
  a: UserAppearance | null,
  b: UserAppearance | null
): boolean {
  if (a === b) return true;
  if (!a || !b) return false;
  return APPEARANCE_FIELDS.every((field) => a[field] === b[field]);
}

/**
 * AppearanceSelector Component
 * ----------------------------
 * Container component for all user appearance selectors.
 * Displays badge selectors for gender, skin tone, hair color, eye color,
 * height, build, and age range preferences.
 *
 * Features:
 * - Local state for unsaved changes
 * - Explicit "Save Preferences" button
 * - Validation showing which fields are missing
 * - Progress indicator (X of 7 fields selected)
 * - Success feedback after saving
 *
 * These settings are saved to the User model and apply to all identity image generations.
 */
export function AppearanceSelector({
  appearance,
  onSave,
  isSaving = false,
}: AppearanceSelectorProps) {
  // Local state for unsaved changes
  const [localAppearance, setLocalAppearance] = useState<UserAppearance>(
    appearance || {}
  );
  // Track if save was recently successful (for showing success indicator)
  const [showSaveSuccess, setShowSaveSuccess] = useState(false);

  // Sync local state when saved appearance changes (e.g., on initial load or user switch)
  useEffect(() => {
    setLocalAppearance(appearance || {});
    setShowSaveSuccess(false);
  }, [appearance]);

  // Calculate derived state
  const filledCount = useMemo(
    () => countFilledFields(localAppearance),
    [localAppearance]
  );
  const missingFields = useMemo(
    () => getMissingFields(localAppearance),
    [localAppearance]
  );
  const isComplete = filledCount === APPEARANCE_FIELDS.length;
  const isDirty = !appearanceEquals(localAppearance, appearance);

  // Handle field change - updates local state only
  const handleChange = <K extends keyof UserAppearance>(
    field: K,
    value: UserAppearance[K]
  ) => {
    setLocalAppearance((prev) => ({
      ...prev,
      [field]: value,
    }));
    // Clear success indicator when user makes changes
    setShowSaveSuccess(false);
  };

  // Handle save button click
  const handleSave = async () => {
    try {
      await onSave(localAppearance);
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
          How would you like to visualize yourself?
        </h2>
        <Info className="size-4 text-neutral-500 mt-0.5" />
      </div>
      <p className="text-xs text-neutral-500 -mt-4">
        These settings are saved to your user profile
      </p>

      {/* Validation Warning */}
      {!isComplete && (
        <div className="flex items-start gap-2 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
          <AlertCircle className="size-4 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-amber-800 dark:text-amber-200">
            <p className="font-medium">
              Please select all options to enable image generation
            </p>
            <p className="text-xs mt-1 text-amber-700 dark:text-amber-300">
              Missing: {missingFields.join(", ")}
            </p>
          </div>
        </div>
      )}

      {/* Selectors */}
      <div className="space-y-6">
        <GenderSelector
          value={localAppearance.gender}
          onChange={(value) => handleChange("gender", value)}
        />

        <SkinToneSelector
          value={localAppearance.skin_tone}
          onChange={(value) => handleChange("skin_tone", value)}
        />

        <HairColorSelector
          value={localAppearance.hair_color}
          onChange={(value) => handleChange("hair_color", value)}
        />

        <EyeColorSelector
          value={localAppearance.eye_color}
          onChange={(value) => handleChange("eye_color", value)}
        />

        <HeightSelector
          value={localAppearance.height}
          onChange={(value) => handleChange("height", value)}
        />

        <BuildSelector
          value={localAppearance.build}
          onChange={(value) => handleChange("build", value)}
        />

        <AgeRangeSelector
          value={localAppearance.age_range}
          onChange={(value) => handleChange("age_range", value)}
        />
      </div>

      {/* Footer with progress and save button */}
      <div className="flex items-center justify-between pt-4 border-t border-neutral-200 dark:border-neutral-700">
        {/* Progress indicator */}
        <div className="flex items-center gap-2">
          {isComplete ? (
            <Check className="size-4 text-green-600 dark:text-green-400" />
          ) : null}
          <span
            className={`text-sm ${
              isComplete
                ? "text-green-600 dark:text-green-400"
                : "text-neutral-500"
            }`}
          >
            {filledCount} of {APPEARANCE_FIELDS.length} fields selected
          </span>
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
            disabled={!isDirty || isSaving}
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
                Save Preferences
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
