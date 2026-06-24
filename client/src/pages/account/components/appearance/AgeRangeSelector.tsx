import { AGE_RANGE_DISPLAY_NAMES, AgeRange } from "@/enums/appearance/ageRange";
import { type BadgeOption, BadgeSelector } from "./BadgeSelector";

interface AgeRangeSelectorProps {
	value: AgeRange | null | undefined;
	onChange: (value: AgeRange) => void;
}

/**
 * AgeRangeSelector Component
 * ---------------------------
 * Badge selector for age range preference.
 *
 * Used in: AppearanceSelector on Account page.
 */
export function AgeRangeSelector({ value, onChange }: AgeRangeSelectorProps) {
	const options: BadgeOption<AgeRange>[] = Object.values(AgeRange).map(
		(ageRange) => ({
			value: ageRange,
			label: AGE_RANGE_DISPLAY_NAMES[ageRange],
		}),
	);

	return (
		<BadgeSelector<AgeRange>
			label="Age"
			options={options}
			value={value || null}
			onChange={onChange}
		/>
	);
}
