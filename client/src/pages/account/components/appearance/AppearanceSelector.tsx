import { useState, useEffect, useMemo } from "react";
import type { UserAppearance } from "@/types/userAppearance";
import {
  AppearanceFields,
  APPEARANCE_FIELDS,
  appearanceEquals,
  countFilledFields,
  getMissingFields,
} from "./AppearanceFields";
import { Button } from "@/components/ui/button";
import { Save, Check, AlertCircle } from "lucide-react";

interface AppearanceSelectorProps {
  /** Current saved appearance from the user profile */
  appearance: UserAppearance | null;
  /** Callback to save appearance changes */
  onSave: (appearance: UserAppearance) => Promise<void>;
  /** Whether a save operation is in progress */
  isSaving?: boolean;
}

/**
 * AppearanceSelector Component
 * ----------------------------
 * Account-page container around {@link AppearanceFields}. Adds the card chrome,
 * heading, validation warning, progress indicator, and an explicit
 * "Save Preferences" button on top of the bare selectors.
 *
 * Features:
 * - Local state for unsaved changes
 * - Explicit "Save Preferences" button
 * - Validation showing which fields are missing
 * - Progress indicator (X of 7 fields selected)
 * - Success feedback after saving
 *
 * These settings are saved to the User model and apply to all identity image generations.
 *
 * Used in: Account page for appearance customization.
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

  // Sync local state when saved appearance changes (e.g., on initial load)
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

  // Update local state when a field changes; clear the success indicator.
  const handleChange = (next: UserAppearance) => {
    setLocalAppearance(next);
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
    <div className="bg-card rounded-lg border p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start gap-2">
        <h2 className="text-xl font-medium">
          Appearance Preferences
        </h2>
      </div>
      <p className="text-sm text-muted-foreground -mt-4">
        These settings are used to generate personalized identity images
      </p>

      {/* Validation Warning */}
      {!isComplete && (
        <div className="flex items-start gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg">
          <AlertCircle className="size-4 text-amber-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-amber-800">
            <p className="font-medium">
              Please select all options to enable image generation
            </p>
            <p className="text-xs mt-1 text-amber-700">
              Missing: {missingFields.join(", ")}
            </p>
          </div>
        </div>
      )}

      {/* Selectors */}
      <AppearanceFields value={localAppearance} onChange={handleChange} />

      {/* Footer with progress and save button */}
      <div className="flex items-center justify-between pt-4 border-t">
        {/* Progress indicator */}
        <div className="flex items-center gap-2">
          {isComplete ? (
            <Check className="size-4 text-green-600" />
          ) : null}
          <span
            className={`text-sm ${
              isComplete
                ? "text-green-600"
                : "text-muted-foreground"
            }`}
          >
            {filledCount} of {APPEARANCE_FIELDS.length} fields selected
          </span>
        </div>

        {/* Save button */}
        <div className="flex items-center gap-2">
          {showSaveSuccess && (
            <span className="text-sm text-green-600 flex items-center gap-1">
              <Check className="size-4" />
              Saved!
            </span>
          )}
          <Button
            type="button"
            onClick={handleSave}
            disabled={!isDirty || isSaving}
            className="nv-gradient-button text-white gap-2"
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
