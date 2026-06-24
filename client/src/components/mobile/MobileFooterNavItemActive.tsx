/**
 * MobileFooterNavItemActive
 *
 * Purpose:
 * - Renders an active navigation item in the mobile footer.
 * - Displays with royal purple background and rounded corners.
 * - Used when the current route matches the nav item's route.
 *
 * Props:
 * - icon: The icon source path to display
 * - label: The accessibility label for the button
 * - onClick: Function to call when the button is clicked
 */
interface MobileFooterNavItemActiveProps {
	icon: string;
	label: string;
	onClick: () => void;
}

export default function MobileFooterNavItemActive({
	icon,
	label,
	onClick,
}: MobileFooterNavItemActiveProps) {
	// Chat icon is already white, so it doesn't need the brightness filter

	return (
		<button
			type="button"
			onClick={onClick}
			className="flex justify-center items-center aspect-square shrink-0 rounded-full bg-[color:var(--nv-royal-purple)] p-3"
			aria-label={label}
		>
			<img src={icon} alt={label} className="w-8 h-8 brightness-0 invert" />
		</button>
	);
}
