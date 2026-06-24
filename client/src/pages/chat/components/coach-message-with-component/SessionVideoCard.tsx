import { useCoachState } from "@/hooks/use-coach-state";
import { CoachMessage } from "@/pages/chat/components/CoachMessage";
import { SessionVideoModal } from "@/pages/chat/components/coach-message-with-component/SessionVideoModal";
import type { CoachRequest } from "@/types/coachRequest";
import type { ComponentAction, ComponentConfig } from "@/types/componentConfig";
import { Play } from "lucide-react";
import React, { useState } from "react";

/**
 * Coaching Phase Videos — `SessionVideoCard` (PR 16 shell, PR 17 dispatch).
 *
 * Renders the thin video card the LLM (or the welcome / break flow)
 * emits inline in chat:
 *
 *   ┌──────────────────────────────────────┐
 *   │  <Video Name>             [ Watch ]  │
 *   └──────────────────────────────────────┘
 *
 * The button label derives from `coachState.shown_videos`:
 *   - "Watch"        when the video_key has NOT been acknowledged
 *   - "Watch Again"  when it HAS been acknowledged
 *
 * Click → opens the modal player (`SessionVideoModal`). For unacked
 * videos the modal includes a threshold-gated Continue button that
 * dispatches the bundled actions from `config.buttons[0].actions`
 * (PR 17). For acked videos (Watch Again) the modal is replay-only —
 * no Continue, no dispatch. Esc / backdrop / X close fires nothing in
 * either case.
 *
 * Per spec Decision 8 — `Watch Again` keeps its button even on historical
 * cards because it's frontend-only (opens the same modal, no actions
 * fire). This is the intentional deviation from the "strip all buttons
 * from historical components" persistent-component convention.
 */
export interface SessionVideoCardProps {
	coachMessage: React.ReactNode;
	config: ComponentConfig;
	onSendUserMessageToCoach: (request: CoachRequest) => void;
}

function extractContentString(node: React.ReactNode): string {
	// ChatMessages passes `<MarkdownRenderer content={message.content} />` as
	// children. Inspect the `content` prop to decide whether to render a
	// text bubble above the card. Defensive: if the shape changes, fall back
	// to showing the bubble (safer than hiding LLM text).
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

export const SessionVideoCard: React.FC<SessionVideoCardProps> = ({
	coachMessage,
	config,
	onSendUserMessageToCoach,
}) => {
	const { coachState } = useCoachState();
	const [open, setOpen] = useState(false);

	const videoName = config.video_name ?? "Session Video";
	const videoUrl = config.video_url ?? "";
	const videoKey = config.video_key;

	const acknowledged =
		videoKey !== undefined &&
		Array.isArray(coachState?.shown_videos) &&
		coachState?.shown_videos?.includes(videoKey);

	// The server bakes the right action chain into the card's first button:
	// intros get [ACK]; outros get [ACK, START_BREAK]. The FE just forwards.
	const continueActions: ComponentAction[] = config.buttons?.[0]?.actions ?? [];

	const handleContinue = (actions: ComponentAction[]) => {
		onSendUserMessageToCoach({ message: null, actions });
	};

	const textContent = extractContentString(coachMessage);
	const hasText = textContent.trim().length > 0;

	return (
		<div className="_SessionVideoCard-wrapper">
			{hasText && <CoachMessage>{coachMessage}</CoachMessage>}

			<div
				data-testid="session-video-card"
				className="_SessionVideoCard mb-4 p-3.5 pr-4 pl-4 rounded-t-[18px] rounded-br-[18px] rounded-bl-[6px] w-fit max-w-[100%] shadow-sm animate-fadeIn break-words mr-auto flex items-center gap-4"
				style={{
					fontFamily: "'Montserrat', sans-serif",
					backgroundColor: "var(--nv-pale-lavender, #eae6fb)",
				}}
			>
				{/* Circular play-icon "thumbnail" — visual signal that this card is a video. */}
				<button
					type="button"
					aria-label={acknowledged ? "Watch video again" : "Watch video"}
					onClick={() => setOpen(true)}
					className="flex items-center justify-center w-10 h-10 rounded-full transition-colors cursor-pointer shrink-0"
					style={{
						backgroundColor: "var(--nv-royal-purple, #531e96)",
						color: "white",
					}}
					onMouseEnter={(e) => {
						e.currentTarget.style.backgroundColor =
							"var(--nv-violet-blue, #6a5ffb)";
					}}
					onMouseLeave={(e) => {
						e.currentTarget.style.backgroundColor =
							"var(--nv-royal-purple, #531e96)";
					}}
				>
					<Play className="w-5 h-5 ml-0.5" fill="currentColor" />
				</button>
				<span className="text-[18px] font-medium leading-[1.5] text-black">
					{videoName}
				</span>
				<button
					type="button"
					onClick={() => setOpen(true)}
					className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md transition-colors cursor-pointer"
					style={{
						backgroundColor: "var(--nv-royal-purple, #531e96)",
						color: "white",
					}}
					onMouseEnter={(e) => {
						e.currentTarget.style.backgroundColor =
							"var(--nv-violet-blue, #6a5ffb)";
					}}
					onMouseLeave={(e) => {
						e.currentTarget.style.backgroundColor =
							"var(--nv-royal-purple, #531e96)";
					}}
				>
					<Play
						className="w-3.5 h-3.5"
						fill="currentColor"
						aria-hidden="true"
					/>
					{acknowledged ? "Watch Again" : "Watch"}
				</button>
			</div>

			{/* `key` resets useVideoThreshold + the <video> element each time
          the modal is reopened, so the Continue button starts disabled
          again on a second view. */}
			<SessionVideoModal
				key={open ? "open" : "closed"}
				open={open}
				onOpenChange={setOpen}
				videoName={videoName}
				videoUrl={videoUrl}
				acknowledged={acknowledged}
				actions={continueActions}
				onContinue={handleContinue}
			/>
		</div>
	);
};
