import { Textarea } from "@/components/ui/textarea";

interface MoodInputProps {
  value: string | null | undefined;
  onChange: (value: string) => void;
}

/**
 * MoodInput Component
 * ------------------
 * Text input for "How do you feel?" scene question.
 * Allows free-form description of emotional state/feeling for identity visualization.
 */
export function MoodInput({ value, onChange }: MoodInputProps) {
  return (
    <div className="space-y-2">
      <label htmlFor="mood-input" className="text-sm font-medium">
        How do you feel?
      </label>
      <Textarea
        id="mood-input"
        placeholder="e.g., proud and calm, passionate and focused..."
        value={value || ""}
        onChange={(e) => onChange(e.target.value)}
        rows={2}
        className="max-w-2xl"
      />
    </div>
  );
}
