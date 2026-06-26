/**
 * LandingPage
 *
 * Purpose:
 * - Public-facing homepage based on Figma Option 3 design
 * - Showcases identity-based coaching methodology through visual identity cards
 * - Targets users who haven't created accounts yet
 * - Uses PublicLayout for navbar and footer (not included here)
 *
 * Sections (matching Figma Option 3):
 * - Hero with logo, headline, subheadline, and login button
 * - Identity strip (left aligned)
 * - Question: "Do you know who you are?"
 * - Identity strip (center aligned)
 * - Question: "Do you know who you want to be?"
 * - Identity strip (right aligned)
 * - Statement: "NeoVita guides you step by step to your future self."
 * - Closing call-to-action (invite-only: log in / use your invite link)
 */

import LandingHero from "@/pages/landing/components/LandingHero";
import LandingIdentityCarousel from "@/pages/landing/components/LandingIdentityCarousel";
import LandingQuestionSection from "@/pages/landing/components/LandingQuestionSection";
import LandingSignupSection from "@/pages/landing/components/LandingSignupSection";
import LandingStatementSection from "@/pages/landing/components/LandingStatementSection";
import { motion } from "framer-motion";
import {
	jasonImages,
	latrizaImages,
	leighAnnImages,
} from "./data/identityImages";

export default function LandingPage() {
	return (
		<div className="_LandingPage min-h-screen bg-background text-foreground relative flex flex-col">
			{/* Hero Section */}
			<motion.div
				initial={{ y: 32, opacity: 0 }}
				animate={{ y: 0, opacity: 1 }}
				transition={{ duration: 0.6, ease: "easeOut", delay: 0.0 }}
			>
				<LandingHero />
			</motion.div>

			{/* First Identity Carousel - Jason */}
			<motion.div
				initial={{ y: 32, opacity: 0 }}
				animate={{ y: 0, opacity: 1 }}
				transition={{ duration: 0.6, ease: "easeOut", delay: 0.1 }}
			>
				<LandingIdentityCarousel
					images={jasonImages}
					folder="jason"
					alignment="left"
					autoScroll={true}
					scrollSpeed={30}
				/>
			</motion.div>

			{/* First Question */}
			<motion.div
				initial={{ y: 32, opacity: 0 }}
				animate={{ y: 0, opacity: 1 }}
				transition={{ duration: 0.6, ease: "easeOut", delay: 0.2 }}
			>
				<LandingQuestionSection textLines={["Do you know", "who you are?"]} />
			</motion.div>

			{/* Second Identity Carousel - Latriza */}
			<motion.div
				initial={{ y: 32, opacity: 0 }}
				animate={{ y: 0, opacity: 1 }}
				transition={{ duration: 0.6, ease: "easeOut", delay: 0.3 }}
			>
				<LandingIdentityCarousel
					images={latrizaImages}
					folder="latriza"
					alignment="center"
					autoScroll={true}
					scrollSpeed={30}
				/>
			</motion.div>

			{/* Second Question */}
			<motion.div
				initial={{ y: 32, opacity: 0 }}
				animate={{ y: 0, opacity: 1 }}
				transition={{ duration: 0.6, ease: "easeOut", delay: 0.4 }}
			>
				<LandingQuestionSection
					textLines={["Do you know", "who you want to be?"]}
				/>
			</motion.div>

			{/* Third Identity Carousel - Leigh-Ann */}
			<motion.div
				initial={{ y: 32, opacity: 0 }}
				animate={{ y: 0, opacity: 1 }}
				transition={{ duration: 0.6, ease: "easeOut", delay: 0.5 }}
			>
				<LandingIdentityCarousel
					images={leighAnnImages}
					folder="leigh-ann"
					alignment="right"
					autoScroll={true}
					scrollSpeed={30}
				/>
			</motion.div>

			{/* Statement Section */}
			<motion.div
				initial={{ y: 32, opacity: 0 }}
				animate={{ y: 0, opacity: 1 }}
				transition={{ duration: 0.6, ease: "easeOut", delay: 0.6 }}
			>
				<LandingStatementSection text="NeoVita guides you step by step to your future self." />
			</motion.div>

			{/* Closing CTA (invite-only) */}
			<motion.div
				initial={{ y: 32, opacity: 0 }}
				animate={{ y: 0, opacity: 1 }}
				transition={{ duration: 0.6, ease: "easeOut", delay: 0.7 }}
			>
				<LandingSignupSection />
			</motion.div>
			<footer className="flex flex-col gap-8 sm:gap-12 md:gap-16 lg:gap-[100px] items-center px-4 sm:px-6 md:px-12 lg:px-[100px] py-5 sm:py-5 md:py-5 lg:py-5 relative shrink-0 w-full nv-gradient-button">
				<p className="font-medium leading-normal relative shrink-0 text-sm sm:text-sm md:text-sm lg:text-[18px] text-white text-center w-full">
					© 2025 Neovita
				</p>
			</footer>
		</div>
	);
}
