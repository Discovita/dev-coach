import type React from "react";

/**
 * UserMessage Component
 *
 * Displays user messages in the chat interface with Montserrat typography.
 * Matches Figma design specifications:
 * - Font: Montserrat Medium (500 weight)
 * - Font size: 18px
 * - Line height: 1.5
 * - Background: Royal Purple to Violet Blue gradient
 * - Text: White
 */
export const UserMessage: React.FC<
	React.PropsWithChildren<React.HTMLAttributes<HTMLDivElement>>
> = ({ children, ...props }) => (
	<div
		className="_UserMessage mb-4 px-8 py-4 rounded-tl-[20px] rounded-tr-[20px] rounded-bl-[20px] rounded-br-[2px] w-fit max-w-[75%] animate-fadeIn break-words ml-auto text-white text-[18px] font-medium leading-[1.5] shadow-sm"
		style={{
			fontFamily: "'Montserrat', sans-serif",
			background:
				"var(--nv-gradient-primary, linear-gradient(45deg, #531e96 0%, #6a5ffb 100%))",
		}}
		{...props}
	>
		{children}
	</div>
);
