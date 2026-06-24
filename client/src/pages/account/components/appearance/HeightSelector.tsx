import { HEIGHT_DISPLAY_NAMES, Height } from "@/enums/appearance/height";
import { type BadgeOption, BadgeSelector } from "./BadgeSelector";

interface HeightSelectorProps {
	value: Height | null | undefined;
	onChange: (value: Height) => void;
}

/**
 * HeightSelector Component
 * ------------------------
 * Badge selector for height preference.
 *
 * Used in: AppearanceSelector on Account page.
 */
export function HeightSelector({ value, onChange }: HeightSelectorProps) {
	const options: BadgeOption<Height>[] = Object.values(Height).map(
		(height) => ({
			value: height,
			label: HEIGHT_DISPLAY_NAMES[height],
		}),
	);

	return (
		<BadgeSelector<Height>
			label="Height"
			options={options}
			value={value || null}
			onChange={onChange}
		/>
	);
}
