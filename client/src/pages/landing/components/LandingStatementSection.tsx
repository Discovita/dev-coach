/**
 * LandingStatementSection
 *
 * Purpose:
 * - Large text section with gradient text effect for statements
 * - Used for statements like "NeoVita guides you step by step to your future self."
 * - Uses existing gradient text helper class
 */

interface LandingStatementSectionProps {
	text: string;
}

export default function LandingStatementSection({
	text,
}: LandingStatementSectionProps) {
	return (
		<div className="flex flex-col gap-8 sm:gap-12 md:gap-16 lg:gap-[100px] items-center px-4 sm:px-6 md:px-12 lg:px-24 xl:px-[200px] py-12 sm:py-16 md:py-24 lg:py-40 relative shrink-0 w-full bg-gradient-to-b from-[var(--nv-lilac-white)] to-[var(--nv-pale-lavender)]">
			<p className="nv-gradient-text font-medium leading-tight sm:leading-normal relative shrink-0 text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-[64px] text-center w-full px-2 sm:px-4">
				{text}
			</p>
		</div>
	);
}
