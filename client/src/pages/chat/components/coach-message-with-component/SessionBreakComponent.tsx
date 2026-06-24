import { CoachMessage } from "@/pages/chat/components/CoachMessage";
import type { CoachRequest } from "@/types/coachRequest";
import type { ComponentConfig } from "@/types/componentConfig";
import { Coffee } from "lucide-react";
import React from "react";

/**
 * Coaching Phase Videos — `SessionBreakComponent`.
 *
 * Two render modes, branched on `config.closed`:
 *
 * - **Active** (`closed` falsy): full card — coffee icon, "Time for a
 *   Break" heading, descriptive copy, "I'm Ready" button. The button
 *   label + actions are server-baked in `start_break.py`
 *   (`config.buttons[0]`); click dispatches the canned-response pattern
 *   `{message: button.label, actions: button.actions}` so the label
 *   becomes a real user `ChatMessage`.
 *
 * - **Closed** (`config.closed === true`): compact one-line historical
 *   marker — "Took a break · {duration}". `end_break.py` sets `closed`
 *   plus `started_at` + `ended_at` on the same SESSION_BREAK message's
 *   component_config when the user clicks I'm Ready, and strips
 *   `buttons` so the closed card can't redispatch END_BREAK.
 *
 * Composer disabling while the break is open is handled separately by
 * `useComposerDisabled` (reads `coachState.on_break`). If `coachMessage`
 * carries non-empty text it still renders as a normal coach bubble
 * ABOVE the card (active or closed).
 */

function extractContentString(node: React.ReactNode): string {
	// `ChatMessages` passes `<MarkdownRenderer content={message.content} />`
	// as children. Inspect the `content` prop to decide whether to show
	// the coach text bubble above the card (mirrors SessionVideoCard).
	if (React.isValidElement(node)) {
		const props = (node as React.ReactElement).props as
			| { content?: unknown }
			| undefined;
		if (props && typeof props.content === "string") {
			return props.content;
		}
	}
	return "";
}

/**
 * Format a break duration for the closed-state marker.
 * - <60s → "less than a minute"
 * - <60m → "{N} minute(s)"
 * - else → "{H}h {M}m"
 */
function formatDuration(startedAt: string, endedAt: string): string {
	const start = Date.parse(startedAt);
	const end = Date.parse(endedAt);
	if (!Number.isFinite(start) || !Number.isFinite(end) || end < start) {
		return "";
	}
	const totalSec = Math.round((end - start) / 1000);
	if (totalSec < 60) return "less than a minute";
	const totalMin = Math.round(totalSec / 60);
	if (totalMin < 60) return `${totalMin} minute${totalMin === 1 ? "" : "s"}`;
	const hours = Math.floor(totalMin / 60);
	const minutes = totalMin % 60;
	return minutes === 0 ? `${hours}h` : `${hours}h ${minutes}m`;
}

export const SessionBreakComponent: React.FC<{
	coachMessage: React.ReactNode;
	config: ComponentConfig;
	onSendUserMessageToCoach: (request: CoachRequest) => void;
	disabled: boolean;
}> = ({ coachMessage, config, onSendUserMessageToCoach, disabled }) => {
	const textContent = extractContentString(coachMessage);
	const hasText = textContent.trim().length > 0;
	const buttons = config.buttons ?? [];
	const isClosed = config.closed === true;

	// ----- Closed (historical) state -----------------------------------
	if (isClosed) {
		const duration =
			config.started_at && config.ended_at
				? formatDuration(config.started_at, config.ended_at)
				: "";
		return (
			<div className="_SessionBreakComponent-wrapper">
				{hasText && <CoachMessage>{coachMessage}</CoachMessage>}
				<div
					data-testid="session-break-card-closed"
					className="_SessionBreakComponent-closed mb-4 px-4 py-2 rounded-full w-fit mr-auto inline-flex items-center gap-2 shadow-sm animate-fadeIn text-sm text-black/70"
					style={{
						fontFamily: "'Montserrat', sans-serif",
						backgroundColor: "var(--nv-pale-lavender, #eae6fb)",
					}}
				>
					<Coffee
						className="w-4 h-4"
						style={{ color: "var(--nv-royal-purple, #531e96)" }}
						aria-hidden="true"
					/>
					<span>Took a break{duration ? ` · ${duration}` : ""}</span>
				</div>
			</div>
		);
	}

	// ----- Active state -----------------------------------------------
	return (
		<div className="_SessionBreakComponent-wrapper">
			{hasText && <CoachMessage>{coachMessage}</CoachMessage>}

			<div
				data-testid="session-break-card"
				className="_SessionBreakComponent mb-4 p-6 rounded-t-[18px] rounded-br-[18px] rounded-bl-[6px] w-full max-w-md mr-auto shadow-md animate-fadeIn flex flex-col items-center text-center"
				style={{
					fontFamily: "'Montserrat', sans-serif",
					backgroundColor: "var(--nv-pale-lavender, #eae6fb)",
					border: "1px solid var(--nv-royal-purple, #531e96)",
				}}
			>
				<div
					className="flex items-center justify-center w-14 h-14 rounded-full mb-3"
					style={{
						backgroundColor: "var(--nv-royal-purple, #531e96)",
						color: "white",
					}}
					aria-hidden="true"
				>
					<Coffee className="w-7 h-7" />
				</div>

				<h3
					className="text-xl font-semibold leading-tight mb-2"
					style={{ color: "var(--nv-royal-purple, #531e96)" }}
				>
					Time for a Break
				</h3>

				<p className="text-[15px] leading-[1.5] text-black/80 mb-5 max-w-xs">
					Step away for as long as you need. Come back when you&rsquo;re ready
					and rested.
				</p>

				{buttons.length > 0 && (
					<div className="flex flex-wrap gap-2 justify-center w-full">
						{buttons.map((button, index) => (
							<button
								type="button"
								key={index}
								onClick={() =>
									onSendUserMessageToCoach({
										message: button.label,
										actions: button.actions,
									})
								}
								disabled={disabled}
								className="px-5 py-2.5 text-base font-medium rounded-md transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
								style={{
									backgroundColor: "var(--nv-royal-purple, #531e96)",
									color: "white",
								}}
								onMouseEnter={(e) => {
									if (e.currentTarget.disabled) return;
									e.currentTarget.style.backgroundColor =
										"var(--nv-violet-blue, #6a5ffb)";
								}}
								onMouseLeave={(e) => {
									e.currentTarget.style.backgroundColor =
										"var(--nv-royal-purple, #531e96)";
								}}
							>
								{button.label}
							</button>
						))}
					</div>
				)}
			</div>
		</div>
	);
};
