import { useRouterState, useNavigate } from "@tanstack/react-router";
import { toast } from "sonner";
import type { NavItem } from "@/types/navItem";
import { useCoachState } from "@/hooks/use-coach-state";
import { isStudioLocked, STUDIO_LOCKED_MESSAGE } from "@/lib/studio-lock";
import MobileFooterNavItemActive from "./MobileFooterNavItemActive";
import MobileFooterNavItemInactive from "./MobileFooterNavItemInactive";

/**
 * MobileAuthFooter
 *
 * Purpose:
 * - Provides the mobile footer navigation for the authenticated application.
 * - Displays navigation items (Chat, Identities, Gallery) with icons.
 * - Fixed at the bottom of the screen on mobile devices.
 * - Shows active state with royal purple background, inactive with pale fill.
 */
export default function MobileAuthFooter() {
  const routerState = useRouterState();
  const pathname = routerState.location.pathname;
  const navigate = useNavigate();
  const { coachState } = useCoachState();
  const studioLocked = isStudioLocked(coachState);

  const navItems: Array<NavItem> = [
    {
      to: "/identities",
      label: "Identities",
      icon: "/users-round.svg",
    },
    { to: "/chat", label: "Chat", icon: "/ai-bubble-white.svg" },
    { to: "/iams", label: "I Am's", icon: "/list.svg" },
    { to: "/studio", label: "Studio", icon: "/brush.svg", locked: studioLocked },
  ];

  return (
    <footer
      className="_MobileAuthFooter sm:hidden fixed bottom-0 left-0 right-0 z-50 h-20 flex items-center justify-center px-6 py-4 gap-14"
      style={{
        background:
          "linear-gradient(220deg, var(--nv-royal-purple, #531E96) -34.16%, var(--nv-violet-blue, #6A5FFB) 50%)",
      }}
    >
      {navItems.map(({ to, label, icon, locked }) => {
        const isActive = pathname === to || pathname.startsWith(to + "/");
        // Chat icon: always use white icon
        const iconSrc = icon;

        const handleClick = () => {
          if (locked) {
            toast(STUDIO_LOCKED_MESSAGE);
            return;
          }
          navigate({ to });
        };

        return isActive ? (
          <MobileFooterNavItemActive
            key={to}
            icon={iconSrc}
            label={label}
            onClick={handleClick}
          />
        ) : (
          <MobileFooterNavItemInactive
            key={to}
            icon={iconSrc}
            label={label}
            locked={locked}
            onClick={handleClick}
          />
        );
      })}
    </footer>
  );
}
