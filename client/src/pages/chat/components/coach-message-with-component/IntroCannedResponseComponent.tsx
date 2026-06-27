import type { CoachRequest } from "@/types/coachRequest";
import type { ComponentConfig } from "@/types/componentConfig";
import MarkdownRenderer from "@/utils/MarkdownRenderer";
import { motion } from "framer-motion";
import React, { useState } from "react";

type ChoiceButton = NonNullable<ComponentConfig["buttons"]>[number];

// Ordered choreography after a click (all tunable):
//   1. un-chosen options fade out slowly; the chosen one holds still
//   2. once they're gone, the chosen option slides into the reply position
//   3. then we dispatch (the real user message takes its place + the coach replies)
const FADE_MS = 1000; // step 1: slow fade of the un-chosen options
const SLIDE_MS = 2000; // step 2: chosen option slides into place

// The chosen option is styled to MATCH a real user message so that when it
// slides into the reply position it already looks like the message it becomes.
const USER_BUBBLE_CLASS =
	"py-3.5 px-4 rounded-tl-[20px] rounded-tr-[20px] rounded-bl-[20px] rounded-br-[2px] w-fit max-w-[75%] break-words text-left text-white text-[18px] font-medium leading-[1.5] shadow-sm";
const USER_BUBBLE_STYLE: React.CSSProperties = {
	fontFamily: "'Montserrat', sans-serif",
	background:
		"var(--nv-gradient-primary, linear-gradient(45deg, #531e96 0%, #6a5ffb 100%))",
};

/**
 * The option buttons for a canned response, rendered as a right-aligned stack
 * of user-message-styled bubbles BENEATH the coach text bubble (a sibling, not
 * a child — so the coach bubble never resizes).
 *
 * On click the steps run strictly in order: the un-chosen options fade out
 * slowly while the chosen one stays put; only once they're gone does the chosen
 * option slide (via `layout`) up into the reply position; then we dispatch, and
 * the real user message takes over in the same spot.
 */
const ChoiceButtons: React.FC<{
	buttons: ChoiceButton[];
	disabled: boolean;
	onChoose: (request: CoachRequest) => void;
}> = ({ buttons, disabled, onChoose }) => {
	const [chosenIndex, setChosenIndex] = useState<number | null>(null);
	// "fading" → un-chosen are fading (still occupying space so the chosen holds
	// still). "sliding" → un-chosen removed; the chosen slides into place.
	const [phase, setPhase] = useState<"idle" | "fading" | "sliding">("idle");

	const handleChoose = (index: number, button: ChoiceButton) => {
		if (chosenIndex !== null || disabled) return;
		setChosenIndex(index);
		setPhase("fading");
		window.setTimeout(() => setPhase("sliding"), FADE_MS);
		window.setTimeout(() => {
			onChoose({ message: button.label, actions: button.actions });
		}, FADE_MS + SLIDE_MS);
	};

	return (
		<div className="mb-4 flex flex-wrap items-center justify-end gap-2">
			{buttons.map((button, index) => {
				const isChosen = index === chosenIndex;
				// Drop the un-chosen options only once they've finished fading, so the
				// chosen one doesn't shift while they fade — then its position change
				// (via `layout`) is the slide into place.
				if (phase === "sliding" && !isChosen) return null;
				const fadingOut = phase !== "idle" && !isChosen;
				return (
					<motion.button
						type="button"
						// biome-ignore lint/suspicious/noArrayIndexKey: buttons are a fixed, ordered list
						key={index}
						layout
						initial={{ opacity: 0, y: 4 }}
						animate={{ opacity: fadingOut ? 0 : 1, y: 0 }}
						transition={{
							opacity: { duration: fadingOut ? FADE_MS / 1000 : 0.25 },
							layout: { duration: SLIDE_MS / 1000, ease: "easeInOut" },
							default: { duration: 0.25 },
						}}
						onClick={() => handleChoose(index, button)}
						disabled={disabled || chosenIndex !== null}
						className={`${USER_BUBBLE_CLASS} cursor-pointer transition-[filter] hover:brightness-110 disabled:cursor-default`}
						style={USER_BUBBLE_STYLE}
					>
						{button.label}
					</motion.button>
				);
			})}
		</div>
	);
};

/**
 * A canned-response coach turn: a fixed coach text bubble plus, optionally, a
 * separate stack of option bubbles. Keeping the options OUT of the bubble means
 * the bubble is laid out once and never resized — answering only removes the
 * sibling options, it doesn't reflow the coach text.
 */
export const IntroCannedResponseComponent: React.FC<{
	coachMessage: React.ReactNode;
	config: ComponentConfig;
	onSendUserMessageToCoach: (request: CoachRequest) => void;
	disabled: boolean;
}> = ({ coachMessage, config, onSendUserMessageToCoach, disabled }) => {
	const buttons = config.buttons;
	const hasButtons = Boolean(buttons && buttons.length > 0);

	return (
		<div className="_IntroCannedResponseComponent">
			{/* Fixed-size coach text bubble — never resizes when options appear or
			    leave (they're a sibling below, not a child). */}
			<div
				className="mb-2 p-3.5 pr-4 pl-4 rounded-t-[18px] rounded-br-[18px] rounded-bl-[6px] w-fit max-w-[75%] shadow-sm break-words mr-auto text-[18px] font-medium leading-[1.5] text-black"
				style={{
					fontFamily: "'Montserrat', sans-serif",
					backgroundColor: "var(--nv-pale-lavender, #eae6fb)",
				}}
			>
				{React.isValidElement(coachMessage) ? (
					coachMessage
				) : (
					<MarkdownRenderer content={String(coachMessage)} />
				)}
			</div>

			{hasButtons && buttons && (
				<ChoiceButtons
					buttons={buttons}
					disabled={disabled}
					onChoose={onSendUserMessageToCoach}
				/>
			)}
		</div>
	);
};
