import { Link } from "@tanstack/react-router";

/**
 * MobileAuthHeader
 *
 * Purpose:
 * - Provides the mobile header for the authenticated application.
 * - Displays the "neovita" brand text centered in the header.
 * - Fixed at the top of the screen on mobile devices.
 * - Includes a settings icon on the right that navigates to the account page.
 */
export default function MobileAuthHeader() {
	const nvLogoSmall = "/neovita_logo_small.png";
	return (
		<header
			className="_MobileAuthHeader sm:hidden fixed top-0 left-0 right-0 z-50 h-20 flex items-center justify-between px-6 py-4"
			style={{
				background:
					"linear-gradient(356deg, var(--nv-royal-purple, #531E96) -85.85%, var(--nv-violet-blue, #6A5FFB) 49.91%)",
			}}
		>
			<img src={nvLogoSmall} alt="Neovita" className="h-8 w-8 flex-shrink-0" />
			<p
				className="text-[32px] text-white font-medium whitespace-nowrap flex-1 text-center"
				style={{
					fontFamily: "'Montserrat', sans-serif",
				}}
			>
				neovita
			</p>
			<Link
				to="/account"
				className="h-8 w-8 flex-shrink-0 flex items-center justify-center cursor-pointer"
				aria-label="Account settings"
			>
				<img
					src="/baseline-settings.svg"
					alt="Settings"
					className="h-8 w-8"
					style={{ filter: "brightness(0) invert(1)" }}
				/>
			</Link>
		</header>
	);
}
