import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { MultiSelect } from "@/components/ui/multi-select";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import { CoachingPhase } from "@/enums/coachingPhase";
import {
	GetToKnowYouQuestions,
	getGetToKnowYouQuestionDisplayName,
} from "@/enums/getToKnowYouQuestions";
import { IdentityCategory } from "@/enums/identityCategory";
import type {
	TestScenarioCoachState,
	TestScenarioIdentity,
} from "@/types/testScenario";
import { useState } from "react";

interface CoachStateFormProps {
	value: TestScenarioCoachState;
	onChange: (value: TestScenarioCoachState) => void;
	identities?: TestScenarioIdentity[];
}

const phaseOptions = Object.values(CoachingPhase).map((v) => ({
	value: v,
	label: v.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
}));
const categoryOptions = Object.values(IdentityCategory).map((v) => ({
	value: v,
	label: v.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
}));

function CoachStateListField({
	label,
	items,
	onAdd,
	onDelete,
	placeholder,
}: {
	label: string;
	items: string[];
	onAdd: (item: string) => void;
	onDelete: (index: number) => void;
	placeholder?: string;
}) {
	const [input, setInput] = useState("");
	return (
		<div className="mb-4">
			<Label className="block mb-1">{label}</Label>
			<div className="flex flex-wrap gap-2 mb-2">
				{items.map((item, idx) => (
					<span
						key={idx}
						className="inline-flex items-center bg-muted text-foreground rounded px-2 py-1 text-xs"
					>
						{item}
						<Button
							type="button"
							size="xs"
							variant="ghost"
							className="ml-1 px-1"
							onClick={() => onDelete(idx)}
						>
							×
						</Button>
					</span>
				))}
			</div>
			<div className="flex gap-2">
				<Input
					value={input}
					onChange={(e) => setInput(e.target.value)}
					onKeyDown={(e) => {
						if (e.key === "Enter" && input.trim()) {
							onAdd(input.trim());
							setInput("");
							e.preventDefault();
						}
					}}
					placeholder={placeholder}
					className="flex-1"
				/>
				<Button
					type="button"
					size="sm"
					onClick={() => {
						if (input.trim()) {
							onAdd(input.trim());
							setInput("");
						}
					}}
				>
					Add
				</Button>
			</div>
		</div>
	);
}

const TestScenarioCoachStateForm = ({
	value,
	onChange,
	identities = [],
}: CoachStateFormProps) => {
	const handleField = <K extends keyof TestScenarioCoachState>(
		key: K,
		val: TestScenarioCoachState[K],
	) => {
		onChange({ ...value, [key]: val });
	};

	return (
		<div className="flex flex-col gap-4">
			<div>
				<Label className="mb-2">Current Phase</Label>
				<Select
					value={value.current_phase || ""}
					onValueChange={(v) =>
						handleField("current_phase", v as CoachingPhase)
					}
				>
					<SelectTrigger className="w-full mt-1">
						<SelectValue placeholder="Select phase" />
					</SelectTrigger>
					<SelectContent>
						{phaseOptions.map((opt) => (
							<SelectItem key={opt.value} value={opt.value}>
								{opt.label}
							</SelectItem>
						))}
					</SelectContent>
				</Select>
			</div>
			<div>
				<Label className="mb-2">
					Current Identity (which Identity is currently being
					refined/affirmed/visualized)
				</Label>
				<p className="text-sm text-muted-foreground mb-2">
					Select from identities defined in the Identities tab. This field will
					be empty if no identities are available.
				</p>
				<Select
					value={value.current_identity || undefined}
					onValueChange={(v) =>
						handleField("current_identity", v === "none" ? undefined : v)
					}
				>
					<SelectTrigger className="w-full mt-1">
						<SelectValue placeholder="Select current identity" />
					</SelectTrigger>
					<SelectContent>
						<SelectItem value="none">None</SelectItem>
						{identities.map((identity) => (
							<SelectItem key={identity.name} value={identity.name}>
								{identity.name} ({identity.category})
							</SelectItem>
						))}
					</SelectContent>
				</Select>
			</div>
			<div>
				<Label className="mb-2">Identity Focus</Label>
				<Select
					value={value.identity_focus || ""}
					onValueChange={(v) =>
						handleField("identity_focus", v as IdentityCategory)
					}
				>
					<SelectTrigger className="w-full mt-1">
						<SelectValue placeholder="Select identity focus" />
					</SelectTrigger>
					<SelectContent>
						{categoryOptions.map((opt) => (
							<SelectItem key={opt.value} value={opt.value}>
								{opt.label}
							</SelectItem>
						))}
					</SelectContent>
				</Select>
			</div>
			<div>
				<Label className="mb-2">Skipped Identity Categories</Label>
				<MultiSelect
					options={categoryOptions}
					value={value.skipped_identity_categories || []}
					onValueChange={(vals) =>
						handleField(
							"skipped_identity_categories",
							vals as IdentityCategory[],
						)
					}
					placeholder="Select categories to skip"
				/>
			</div>
			<CoachStateListField
				label="Who You Are"
				items={value.who_you_are || []}
				onAdd={(item) =>
					handleField("who_you_are", [...(value.who_you_are || []), item])
				}
				onDelete={(idx) =>
					handleField(
						"who_you_are",
						(value.who_you_are || []).filter((_, i) => i !== idx),
					)
				}
				placeholder="Add a trait or description"
			/>
			<CoachStateListField
				label="Who You Want To Be"
				items={value.who_you_want_to_be || []}
				onAdd={(item) =>
					handleField("who_you_want_to_be", [
						...(value.who_you_want_to_be || []),
						item,
					])
				}
				onDelete={(idx) =>
					handleField(
						"who_you_want_to_be",
						(value.who_you_want_to_be || []).filter((_, i) => i !== idx),
					)
				}
				placeholder="Add a trait or aspiration"
			/>
			<div>
				<Label className="mb-2">Asked Questions</Label>
				<MultiSelect
					options={Object.values(GetToKnowYouQuestions).map((question) => ({
						value: question,
						label: getGetToKnowYouQuestionDisplayName(question),
					}))}
					value={value.asked_questions || []}
					onValueChange={(vals) =>
						handleField("asked_questions", vals as GetToKnowYouQuestions[])
					}
					placeholder="Select questions that have been asked"
				/>
			</div>
			<CoachStateListField
				label="Shown Videos (Coaching Phase Videos)"
				items={value.shown_videos || []}
				onAdd={(item) =>
					handleField("shown_videos", [...(value.shown_videos || []), item])
				}
				onDelete={(idx) =>
					handleField(
						"shown_videos",
						(value.shown_videos || []).filter((_, i) => i !== idx),
					)
				}
				placeholder="e.g. welcome_session_intro, get_to_know_session_outro"
			/>
		</div>
	);
};

export default TestScenarioCoachStateForm;
