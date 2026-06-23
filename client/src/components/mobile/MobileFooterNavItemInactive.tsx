import { Lock } from "lucide-react";

/**
 * MobileFooterNavItemInactive
 *
 * Purpose:
 * - Renders an inactive navigation item in the mobile footer.
 * - Displays with pale fill background in a 60x60px square.
 * - Used when the current route does not match the nav item's route.
 *
 * Props:
 * - icon: The icon source path to display
 * - label: The accessibility label for the button
 * - locked: When true, overlays a lock badge and dims the icon
 * - onClick: Function to call when the button is clicked
 */
interface MobileFooterNavItemInactiveProps {
  icon: string;
  label: string;
  locked?: boolean;
  onClick: () => void;
}

export default function MobileFooterNavItemInactive({
  icon,
  label,
  locked,
  onClick,
}: MobileFooterNavItemInactiveProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex justify-center items-center aspect-square shrink-0 rounded-full w-[60px] h-[60px] bg-[color:var(--nv-pale-lavender-50)]"
      aria-label={label}
    >
      <span className="relative inline-flex">
        <img
          src={icon}
          alt={label}
          className={`w-8 h-8 brightness-0 invert ${locked ? "opacity-60" : ""}`}
        />
        {locked && (
          <Lock className="absolute -bottom-1 -right-1 w-4 h-4 text-[color:var(--nv-royal-purple)]" />
        )}
      </span>
    </button>
  );
}
