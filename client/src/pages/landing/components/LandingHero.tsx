/**
 * LandingHero
 *
 * Purpose:
 * - Hero section for the landing page based on Figma Option 3 design
 * - Features full-bleed background with gradient overlay, centered logo, headline, and login button
 * - Uses existing brand tokens and gradient helpers
 */

import { Link } from "@tanstack/react-router";

// Image assets - these will need to be replaced with actual hero background images
// For now using placeholder structure that matches Figma design
const heroBackgroundImage = "/landing/hero-background.png";
const heroOverlayImage = "/landing/hero-overlay.png";
const logoImage = "/neovita_logo_large.png";

export default function LandingHero() {
  return (
    <section className="relative w-full">
      <div className="flex flex-col gap-12 sm:gap-16 md:gap-20 lg:gap-[100px] items-center px-2 sm:px-6 md:px-8 lg:p-10 py-2 sm:py-10 md:py-10 relative w-full">
        {/* Hero card with background */}
        <div className="flex flex-col min-h-[400px] sm:min-h-[500px] md:min-h-[600px] lg:h-[760px] items-end overflow-hidden p-3 sm:p-4 md:p-5 relative rounded-2xl sm:rounded-[24px] md:rounded-[30px] w-full">
          {/* Background layers */}
          <div aria-hidden="true" className="absolute inset-0 pointer-events-none rounded-2xl sm:rounded-[24px] md:rounded-[30px]">
            <div className="absolute inset-0 opacity-60 overflow-hidden rounded-2xl sm:rounded-[24px] md:rounded-[30px]">
              <img
                alt=""
                className="absolute h-[457.24%] left-[-17.53%] max-w-none top-[-20.66%] w-[134.48%]"
                src={heroBackgroundImage}
              />
            </div>
            <img
              alt=""
              className="absolute max-w-none object-cover rounded-2xl sm:rounded-[24px] md:rounded-[30px] size-full"
              src={heroOverlayImage}
            />
          </div>

          {/* Login button - top right */}
          <Link
            to="/login"
            className="flex gap-2 h-10 sm:h-12 md:h-[52px] items-center justify-end overflow-hidden px-4 sm:px-6 md:px-8 py-2 sm:py-3 md:py-4 relative rounded-full shrink-0 z-10 nv-gradient-button text-sm sm:text-base"
          >
            <p className="font-semibold leading-none relative shrink-0 text-center text-nowrap text-white whitespace-pre">
              Login
            </p>
          </Link>

          {/* Centered content */}
          <div className="flex flex-col gap-8 sm:gap-12 md:gap-16 lg:gap-[100px] grow items-center justify-center min-h-px min-w-px pb-12 sm:pb-20 md:pb-32 lg:pb-40 pt-0 px-4 sm:px-6 md:px-8 lg:px-0 relative shrink-0 w-full">
            {/* Logo and brand name */}
            <div className="flex flex-col gap-2 sm:gap-3 md:gap-4 items-center relative shrink-0 w-full">
              <div className="h-16 sm:h-20 md:h-24 lg:h-[98.982px] w-auto aspect-square relative shrink-0">
                <img
                  alt="Neovita logo"
                  className="absolute inset-0 max-w-none object-contain pointer-events-none size-full lg:mt-5"
                  src={logoImage}
                />
              </div>
              <p className="font-medium leading-normal not-italic relative shrink-0 text-2xl sm:text-3xl md:text-4xl lg:text-[44px] text-[color:var(--nv-indigo)] text-center">
                neovita
              </p>
            </div>

            {/* Headline and subheadline */}
            <div className="flex flex-col gap-4 sm:gap-6 md:gap-8 lg:gap-10 items-center leading-normal relative shrink-0 text-[color:var(--nv-indigo)] text-center w-full px-2 sm:px-4">
              <div className="font-bold relative shrink-0 text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-[66px] tracking-tight sm:tracking-[0.5px] md:tracking-[1px] lg:tracking-[1.32px] max-w-full">
                <p className="mb-0">Guided by AI,</p>
                <p>created for your evolution.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
