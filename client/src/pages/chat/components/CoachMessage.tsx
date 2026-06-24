import type React from "react";

/**
 * CoachMessage Component
 *
 * Displays coach messages in the chat interface with Montserrat typography.
 * Matches Figma design specifications:
 * - Font: Montserrat Medium (500 weight)
 * - Font size: 18px
 * - Line height: 1.5
 * - Background: Pale Lavender (#eae6fb)
 * - Text: Black
 */
export const CoachMessage: React.FC<
	React.PropsWithChildren<React.HTMLAttributes<HTMLDivElement>>
> = ({ children, ...props }) => (
	<div
		className="_CoachMessage mb-4 p-3.5 pr-4 pl-4 rounded-t-[18px] rounded-br-[18px] rounded-bl-[6px] w-fit max-w-[75%] shadow-sm animate-fadeIn break-words mr-auto text-[18px] font-medium leading-[1.5] text-black"
		style={{
			fontFamily: "'Montserrat', sans-serif",
			backgroundColor: "var(--nv-pale-lavender, #eae6fb)",
		}}
		{...props}
	>
		{children}
	</div>
);
