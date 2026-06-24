import { GENDER_DISPLAY_NAMES, Gender } from "@/enums/appearance/gender";
import { type BadgeOption, BadgeSelector } from "./BadgeSelector";

interface GenderSelectorProps {
	value: Gender | null | undefined;
	onChange: (value: Gender) => void;
}

/**
 * GenderSelector Component
 * -----------------------
 * Badge selector for gender preference (man, woman, person).
 *
 * Used in: AppearanceSelector on Account page.
 */
export function GenderSelector({ value, onChange }: GenderSelectorProps) {
	const options: BadgeOption<Gender>[] = Object.values(Gender).map(
		(gender) => ({
			value: gender,
			label: GENDER_DISPLAY_NAMES[gender],
		}),
	);

	return (
		<BadgeSelector<Gender>
			label="Gender"
			options={options}
			value={value || null}
			onChange={onChange}
		/>
	);
}
