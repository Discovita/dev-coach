import type { CoachRequest } from "@/types/coachRequest";
import type { ComponentConfig } from "@/types/componentConfig";
import MarkdownRenderer from "@/utils/MarkdownRenderer";
import React from "react";

export const IntroCannedResponseComponent: React.FC<{
	coachMessage: React.ReactNode;
	config: ComponentConfig;
	onSendUserMessageToCoach: (request: CoachRequest) => void;
	disabled: boolean;
}> = ({ coachMessage, config, onSendUserMessageToCoach, disabled }) => {
	const hasButtons = config.buttons && config.buttons.length > 0;

	return (
		<div
			className={`_IntroCannedResponseComponent mb-4 p-3.5 pr-4 pl-4 rounded-t-[18px] rounded-br-[18px] rounded-bl-[6px] ${
				hasButtons ? "w-fit max-w-[100%]" : "w-fit max-w-[75%]"
			} shadow-sm animate-fadeIn break-words mr-auto text-[18px] font-medium leading-[1.5] text-black`}
			style={{
				fontFamily: "'Montserrat', sans-serif",
				backgroundColor: "var(--nv-pale-lavender, #eae6fb)",
			}}
		>
			<div>
				{React.isValidElement(coachMessage) ? (
					coachMessage
				) : (
					<MarkdownRenderer content={String(coachMessage)} />
				)}
			</div>

			{config.buttons && config.buttons.length > 0 && (
				<div className="mt-3 flex flex-wrap gap-2 justify-end">
					{config.buttons.map((button, index) => (
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
							className="px-3 py-1.5 text-sm font-medium rounded-md transition-colors cursor-pointer"
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
							{button.label}
						</button>
					))}
				</div>
			)}
		</div>
	);
};
