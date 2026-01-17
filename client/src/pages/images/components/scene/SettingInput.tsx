import { Textarea } from "@/components/ui/textarea";

interface SettingInputProps {
  value: string | null | undefined;
  onChange: (value: string) => void;
  disabled?: boolean;
}

/**
 * SettingInput Component
 * ---------------------
 * Text input for "What is the setting?" scene question.
 * Allows free-form description of environment/location for identity visualization.
 */
export function SettingInput({ value, onChange, disabled = false }: SettingInputProps) {
  return (
    <div className="space-y-2">
      <label htmlFor="setting-input" className="text-sm font-medium">
        What is the setting?
      </label>
      <Textarea
        id="setting-input"
        placeholder="e.g., on a hill overlooking Hawaiian agricultural land with view of the ocean..."
        value={value || ""}
        onChange={(e) => onChange(e.target.value)}
        rows={3}
        className="max-w-2xl"
        disabled={disabled}
      />
    </div>
  );
}
