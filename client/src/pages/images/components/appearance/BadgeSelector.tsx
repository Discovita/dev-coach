import { cn } from "@/lib/utils";

/**
 * BadgeSelector Component
 * -----------------------
 * Reusable badge selector component for appearance options.
 * Displays options as clickable badges with selected state styling.
 */
export interface BadgeOption<T extends string = string> {
  value: T;
  label: string;
  color?: string; // Optional color for visual representation (e.g., skin tone)
}

interface BadgeSelectorProps<T extends string = string> {
  label: string;
  options: BadgeOption<T>[];
  value: T | null | undefined;
  onChange: (value: T) => void;
  className?: string;
}

export function BadgeSelector<T extends string = string>({
  label,
  options,
  value,
  onChange,
  className,
}: BadgeSelectorProps<T>) {
  return (
    <div className={cn("space-y-2", className)}>
      <label className="text-sm font-medium">{label}</label>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            className={cn(
              "px-3 py-1.5 rounded-full text-sm font-medium transition-all",
              "border-2",
              value === option.value
                ? "border-gold-500 bg-gold-500 text-black dark:bg-gold-600 dark:text-white"
                : "border-neutral-300 bg-background hover:border-gold-400/50 dark:border-neutral-700 dark:hover:border-gold-500/50"
            )}
            style={
              option.color && value === option.value
                ? { backgroundColor: option.color, color: "#000" }
                : option.color && value !== option.value
                ? { borderColor: option.color, backgroundColor: "transparent" }
                : undefined
            }
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}
