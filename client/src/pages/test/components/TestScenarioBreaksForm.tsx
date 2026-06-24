import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { TestScenarioBreak } from "@/types/testScenario";
import { useRef, useState } from "react";

interface Props {
	value: TestScenarioBreak[];
	onChange: (breaks: TestScenarioBreak[]) => void;
}

const EMPTY_DRAFT: TestScenarioBreak = {
	triggered_by_session: "",
	started_at: "",
	ended_at: "",
	original_coach_message_id: "",
};

/**
 * Coaching Phase Videos — Break editor for the TestScenario template.
 *
 * Open break: `ended_at` empty (drives `on_break=true` in the
 * instantiated scenario).
 * Closed break: both `started_at` and `ended_at` set.
 *
 * `original_coach_message_id` is the UUID of the SESSION_BREAK coach
 * message in `template.chat_messages` — used by
 * `resolve_scenario_coach_message` to relink the FK at instantiation.
 * Optional; leave blank if there's no corresponding chat message to
 * anchor to.
 */
export default function TestScenarioBreaksForm({ value, onChange }: Props) {
	const parentRef = useRef<HTMLDivElement>(null);
	const [draft, setDraft] = useState<TestScenarioBreak>(EMPTY_DRAFT);
	const [editingIndex, setEditingIndex] = useState<number | null>(null);

	function clean(d: TestScenarioBreak): TestScenarioBreak {
		// Strip empty optional fields so the saved template matches what
		// the backend serializer expects (omit absent rather than send "").
		const out: TestScenarioBreak = {
			triggered_by_session: d.triggered_by_session.trim(),
		};
		if (d.started_at?.trim()) out.started_at = d.started_at.trim();
		if (d.ended_at?.trim()) out.ended_at = d.ended_at.trim();
		if (d.original_coach_message_id?.trim()) {
			out.original_coach_message_id = d.original_coach_message_id.trim();
		}
		return out;
	}

	const handleSave = () => {
		if (!draft.triggered_by_session.trim()) return;
		const next = clean(draft);
		if (editingIndex !== null) {
			onChange(value.map((b, i) => (i === editingIndex ? next : b)));
			setEditingIndex(null);
		} else {
			onChange([...value, next]);
		}
		setDraft(EMPTY_DRAFT);
	};

	const handleEdit = (idx: number) => {
		setEditingIndex(idx);
		setDraft({
			triggered_by_session: value[idx].triggered_by_session ?? "",
			started_at: value[idx].started_at ?? "",
			ended_at: value[idx].ended_at ?? "",
			original_coach_message_id: value[idx].original_coach_message_id ?? "",
		});
	};

	const handleDelete = (idx: number) => {
		onChange(value.filter((_, i) => i !== idx));
		if (editingIndex === idx) {
			setEditingIndex(null);
			setDraft(EMPTY_DRAFT);
		}
	};

	const handleCancelEdit = () => {
		setEditingIndex(null);
		setDraft(EMPTY_DRAFT);
	};

	return (
		<div className="flex flex-col gap-4">
			<div className="grid grid-cols-1 md:grid-cols-2 gap-3 items-end">
				<div>
					<Label className="mb-2">Triggered By Session *</Label>
					<Input
						value={draft.triggered_by_session}
						onChange={(e) =>
							setDraft((d) => ({ ...d, triggered_by_session: e.target.value }))
						}
						placeholder="e.g. get_to_know_session"
					/>
				</div>
				<div>
					<Label className="mb-2">Original Coach Message ID</Label>
					<Input
						value={draft.original_coach_message_id ?? ""}
						onChange={(e) =>
							setDraft((d) => ({
								...d,
								original_coach_message_id: e.target.value,
							}))
						}
						placeholder="UUID of the SESSION_BREAK message (optional)"
					/>
				</div>
				<div>
					<Label className="mb-2">Started At</Label>
					<Input
						type="datetime-local"
						value={draft.started_at ?? ""}
						onChange={(e) =>
							setDraft((d) => ({ ...d, started_at: e.target.value }))
						}
					/>
				</div>
				<div>
					<Label className="mb-2">
						Ended At (leave empty = still on break)
					</Label>
					<Input
						type="datetime-local"
						value={draft.ended_at ?? ""}
						onChange={(e) =>
							setDraft((d) => ({ ...d, ended_at: e.target.value }))
						}
					/>
				</div>
			</div>
			<div className="flex gap-2">
				<Button type="button" onClick={handleSave}>
					{editingIndex !== null ? "Save" : "Add Break"}
				</Button>
				{editingIndex !== null && (
					<Button type="button" variant="secondary" onClick={handleCancelEdit}>
						Cancel Edit
					</Button>
				)}
			</div>
			<div
				ref={parentRef}
				className="overflow-auto border border-border rounded-lg bg-background"
				style={{ height: 360, width: "100%" }}
			>
				{value.length === 0 && (
					<div className="px-4 py-6 text-sm text-muted-foreground text-center">
						No breaks. Add one above to simulate the user being on (or having
						taken) a between-session pause.
					</div>
				)}
				{value.map((br, idx) => {
					const open = !br.ended_at;
					return (
						<div
							key={idx}
							className={[
								"flex items-start gap-3 border-b border-border/50 px-4 py-3 min-h-[48px] box-border w-full",
								idx % 2 === 0 ? "bg-muted/30" : "bg-background",
							].join(" ")}
						>
							<div className="flex-1 min-w-0">
								<div className="flex items-center gap-2">
									<span className="font-medium truncate">
										{br.triggered_by_session || "(no session)"}
									</span>
									<span
										className={[
											"text-xs px-1.5 py-0.5 rounded",
											open
												? "bg-yellow-100 text-yellow-900"
												: "bg-green-100 text-green-900",
										].join(" ")}
									>
										{open ? "open" : "closed"}
									</span>
								</div>
								<div className="text-xs text-muted-foreground mt-1 truncate">
									{br.started_at
										? `Started: ${br.started_at}`
										: "Started: (auto-now)"}
									{br.ended_at ? ` · Ended: ${br.ended_at}` : ""}
								</div>
								{br.original_coach_message_id && (
									<div className="text-xs text-muted-foreground mt-0.5 truncate">
										msg: {br.original_coach_message_id}
									</div>
								)}
							</div>
							<Button
								type="button"
								size="xs"
								variant="secondary"
								onClick={() => handleEdit(idx)}
							>
								Edit
							</Button>
							<Button
								type="button"
								size="xs"
								variant="destructive"
								onClick={() => handleDelete(idx)}
							>
								Delete
							</Button>
						</div>
					);
				})}
			</div>
		</div>
	);
}
