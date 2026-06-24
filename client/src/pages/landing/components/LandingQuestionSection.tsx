/**
 * LandingQuestionSection
 *
 * Purpose:
 * - Large text section with gradient text effect
 * - Used for questions like "Do you know who you are?" and "Do you know who you want to be?"
 * - Uses existing gradient text helper class
 */

interface LandingQuestionSectionProps {
	text?: string;
	textLines?: string[];
}

export default function LandingQuestionSection({
	text,
	textLines,
}: LandingQuestionSectionProps) {
	return (
		<div className="flex flex-col gap-8 sm:gap-12 md:gap-16 lg:gap-[100px] items-center px-4 sm:px-6 md:px-12 lg:px-[100px] py-12 sm:py-16 md:py-24 lg:py-40 relative shrink-0 w-full bg-gradient-to-b from-[var(--nv-lilac-white)] to-[var(--nv-pale-lavender)]">
			<div className="nv-gradient-text font-medium leading-tight sm:leading-normal relative shrink-0 text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-[64px] text-center w-full px-2 sm:px-4">
				{textLines ? (
					<>
						{textLines.map((line, index) => (
							<p key={index} className={index === 0 ? "mb-0" : ""}>
								{line}
							</p>
						))}
					</>
				) : (
					<p>{text || ""}</p>
				)}
			</div>
		</div>
	);
}
