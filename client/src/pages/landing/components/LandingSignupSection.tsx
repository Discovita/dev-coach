/**
 * LandingSignupSection
 *
 * Purpose:
 * - Closing call-to-action on the landing page.
 * - Registration is invite-only, so there is no public signup form here:
 *   visitors are pointed to log in, and invitees use the link in their email.
 * - Uses existing brand tokens and gradient helpers.
 */

import { Button } from "@/components/ui/button";
import { useNavigate } from "@tanstack/react-router";

export default function LandingSignupSection() {
	const navigate = useNavigate();

	return (
		<div className="bg-white flex flex-col gap-12 sm:gap-16 md:gap-20 lg:gap-[100px] items-center p-4 sm:p-6 md:p-12 lg:p-16 xl:p-[100px] relative shrink-0 w-full">
			<div className="flex flex-col gap-6 sm:gap-8 items-center relative shrink-0 w-full max-w-[500px]">
				{/* Headline */}
				<div className="flex flex-col gap-2 items-center relative shrink-0 w-full">
					<p className="font-medium leading-[1.4] relative shrink-0 text-xl sm:text-2xl md:text-3xl lg:text-[36px] text-black text-center w-full">
						Begin your journey to your future self
					</p>
					<p className="font-medium leading-[1.5] relative shrink-0 text-base sm:text-lg md:text-[18px] text-black/60 text-center w-full">
						NeoVita is currently invite-only.
					</p>
				</div>

				{/* Log in CTA */}
				<div className="flex flex-col gap-4 items-center relative shrink-0 w-full">
					<Button
						type="button"
						onClick={() => navigate({ to: "/login" })}
						className="nv-gradient-button w-full rounded-full h-[52px] px-8 text-[20px] font-semibold"
					>
						Log in
					</Button>
					<p className="font-medium leading-[1.5] relative shrink-0 text-sm sm:text-base text-black/50 text-center w-full">
						Have an invite? Use the link in your email to create your account.
					</p>
				</div>
			</div>
		</div>
	);
}
