import {
	HAIR_COLOR_DISPLAY_NAMES,
	HairColor,
} from "@/enums/appearance/hairColor";
import { type BadgeOption, BadgeSelector } from "./BadgeSelector";

interface HairColorSelectorProps {
	value: HairColor | null | undefined;
	onChange: (value: HairColor) => void;
}

/**
 * HairColorSelector Component
 * ---------------------------
 * Badge selector for hair color preference.
 *
 * Used in: AppearanceSelector on Account page.
 */
export function HairColorSelector({ value, onChange }: HairColorSelectorProps) {
	const options: BadgeOption<HairColor>[] = Object.values(HairColor).map(
		(color) => ({
			value: color,
			label: HAIR_COLOR_DISPLAY_NAMES[color],
		}),
	);

	return (
		<BadgeSelector<HairColor>
			label="Hair Color"
			options={options}
			value={value || null}
			onChange={onChange}
		/>
	);
}
