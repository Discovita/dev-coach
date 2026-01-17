import { Textarea } from "@/components/ui/textarea";

interface ClothingInputProps {
  value: string | null | undefined;
  onChange: (value: string) => void;
  disabled?: boolean;
}

/**
 * ClothingInput Component
 * ----------------------
 * Text input for "What are you wearing?" scene question.
 * Allows free-form description of clothing/attire for identity visualization.
 */
export function ClothingInput({ value, onChange, disabled = false }: ClothingInputProps) {
  return (
    <div className="space-y-2">
      <label htmlFor="clothing-input" className="text-sm font-medium">
        What are you wearing?
      </label>
      <Textarea
        id="clothing-input"
        placeholder="e.g., linen button-down shirt, formal conductor's attire..."
        value={value || ""}
        onChange={(e) => onChange(e.target.value)}
        rows={2}
        className="max-w-2xl"
        disabled={disabled}
      />
    </div>
  );
}
