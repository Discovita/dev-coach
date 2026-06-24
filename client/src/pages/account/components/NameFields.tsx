import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export type NameValue = { first_name: string; last_name: string };

/**
 * NameFields Component
 * --------------------
 * Bare first-name / last-name input pair. Presentational only — the parent owns
 * the value and persistence. Shared by the account page (name editing) and the
 * onboarding name-capture step, mirroring how AppearanceFields is reused.
 */
export function NameFields({
	value,
	onChange,
	disabled,
}: {
	value: NameValue;
	onChange: (value: NameValue) => void;
	disabled?: boolean;
}) {
	return (
		<div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
			<div className="space-y-2">
				<Label htmlFor="first_name">First name</Label>
				<Input
					id="first_name"
					value={value.first_name}
					disabled={disabled}
					onChange={(e) => onChange({ ...value, first_name: e.target.value })}
					placeholder="First name"
				/>
			</div>
			<div className="space-y-2">
				<Label htmlFor="last_name">Last name</Label>
				<Input
					id="last_name"
					value={value.last_name}
					disabled={disabled}
					onChange={(e) => onChange({ ...value, last_name: e.target.value })}
					placeholder="Last name"
				/>
			</div>
		</div>
	);
}
