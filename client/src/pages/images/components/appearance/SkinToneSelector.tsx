import { SkinTone, SKIN_TONE_DISPLAY_NAMES, SKIN_TONE_COLORS } from "@/enums/appearance/skinTone";

interface SkinToneSelectorProps {
  value: SkinTone | null | undefined;
  onChange: (value: SkinTone) => void;
}

/**
 * SkinToneSelector Component
 * --------------------------
 * Visual color swatch selector for skin tone preference.
 * Uses circular color swatches with selected state ring.
 */
export function SkinToneSelector({ value, onChange }: SkinToneSelectorProps) {
  const tones = Object.values(SkinTone).map((tone) => ({
    value: tone,
    label: SKIN_TONE_DISPLAY_NAMES[tone],
    color: SKIN_TONE_COLORS[tone],
  }));

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">Skin Tone</label>
      <div className="flex gap-3">
        {tones.map((tone) => (
          <button
            key={tone.value}
            type="button"
            onClick={() => onChange(tone.value)}
            className={`w-10 h-10 rounded-full transition-all border-2 ${
              value === tone.value
                ? "border-gold-500 ring-2 ring-gold-500 ring-offset-2 dark:ring-gold-600"
                : "border-transparent hover:border-neutral-400 dark:hover:border-neutral-600"
            }`}
            style={{ backgroundColor: tone.color }}
            title={tone.label}
            aria-label={tone.label}
          />
        ))}
      </div>
    </div>
  );
}
