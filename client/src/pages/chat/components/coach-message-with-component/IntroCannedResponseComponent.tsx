import type { CoachRequest } from "@/types/coachRequest";
import type { ComponentConfig } from "@/types/componentConfig";
import MarkdownRenderer from "@/utils/MarkdownRenderer";
import { AnimatePresence, motion } from "framer-motion";
import React, { useState } from "react";

type ChoiceButton = NonNullable<ComponentConfig["buttons"]>[number];

// How long the chosen button is allowed to "confirm" (and the others to fade
// out) before we actually dispatch. Keeps the choice from vanishing in the same
// instant it's clicked.
const CHOICE_DISPATCH_DELAY_MS = 260;

/**
 * The option buttons for a canned response. Rendered as a SEPARATE element
 * beneath the coach text bubble (not inside it) so the coach bubble itself
 * never changes size when the options come and go.
 *
 * On click: the un-chosen options fade out, the chosen one briefly confirms,
 * and then — after a short beat — we dispatch. The dispatch flips the card to
 * display-only (these buttons unmount) and the choice reappears as the real
 * user message (which slides in from the right in ChatMessages), so it reads as
 * the option sliding over to become the user's message.
 */
const ChoiceButtons: React.FC<{
	buttons: ChoiceButton[];
	disabled: boolean;
	onChoose: (request: CoachRequest) => void;
}> = ({ buttons, disabled, onChoose }) => {
	const [chosenIndex, setChosenIndex] = useState<number | null>(null);

	const handleChoose = (index: number, button: ChoiceButton) => {
		if (chosenIndex !== null || disabled) return;
		setChosenIndex(index);
		window.setTimeout(() => {
			onChoose({ message: button.label, actions: button.actions });
		}, CHOICE_DISPATCH_DELAY_MS);
	};

	return (
		<div className="mb-4 flex flex-wrap gap-2 justify-end">
			<AnimatePresence>
				{buttons.map((button, index) => {
					// Once chosen, drop the others so they animate out; keep the chosen
					// one until the card flips display-only and this whole row unmounts.
					if (chosenIndex !== null && index !== chosenIndex) return null;
					const isChosen = chosenIndex === index;
					return (
						<motion.button
							type="button"
							// biome-ignore lint/suspicious/noArrayIndexKey: buttons are a fixed, ordered list
							key={index}
							layout
							initial={{ opacity: 0, y: 4 }}
							animate={{ opacity: 1, y: 0, scale: isChosen ? 1.05 : 1 }}
							exit={{ opacity: 0, scale: 0.85 }}
							transition={{ duration: 0.2, ease: "easeOut" }}
							onClick={() => handleChoose(index, button)}
							disabled={disabled || chosenIndex !== null}
							className="px-3 py-1.5 text-sm font-medium rounded-md cursor-pointer disabled:cursor-default"
							style={{
								backgroundColor: "var(--nv-royal-purple, #531e96)",
								color: "white",
							}}
							onMouseEnter={(e) => {
								if (chosenIndex === null)
									e.currentTarget.style.backgroundColor =
										"var(--nv-violet-blue, #6a5ffb)";
							}}
							onMouseLeave={(e) => {
								e.currentTarget.style.backgroundColor =
									"var(--nv-royal-purple, #531e96)";
							}}
						>
							{button.label}
						</motion.button>
					);
				})}
			</AnimatePresence>
		</div>
	);
};

/**
 * A canned-response coach turn: a fixed coach text bubble plus, optionally, a
 * separate row of option buttons. Keeping the buttons OUT of the bubble means
 * the bubble is laid out once and never resized — answering only removes the
 * sibling button row, it doesn't reflow the coach text.
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
			{/* Fixed-size coach text bubble — never resizes when buttons appear or
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
