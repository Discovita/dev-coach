import { useRouterState, useNavigate } from "@tanstack/react-router";
import type { ReactNode } from "react";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FlaskConical, ScrollText, Shield, Users } from "lucide-react";
import MobileAuthHeader from "@/components/mobile/MobileAuthHeader";
import MobileAuthFooter from "@/components/mobile/MobileAuthFooter";
import { useProfile } from "@/hooks/use-profile";
import type { NavItem } from "@/types/navItem";
import { ImpersonationBanner } from "@/components/ImpersonationBanner";

// Toggle icon - local SVG from public directory
const toggleIcon = "/sidebar-toggle.svg";

/**
 * AuthLayout
 *
 * Purpose:
 * - Provides the authenticated application shell with a left sidebar and a main content area.
 * - Hosts navigation links (dummy for now). Child routes render via the route layout's <Outlet />.
 *
 * Usage:
 * - Used as the layout wrapper for authenticated routes via `_authenticated/route.tsx`.
 * - Child routes render inside the main content area through <Outlet />.
 */
/**
 * Admin nav item — uses a React icon component (lucide) instead of an SVG path,
 * so admin items are visually distinguishable and don't require custom SVG assets.
 */
interface AdminNavItem {
  to: string;
  label: string;
  Icon: React.FC<{ className?: string }>;
}

const adminNavItems: AdminNavItem[] = [
  { to: "/admin/users", label: "Users", Icon: Users },
  { to: "/admin/test", label: "Test", Icon: FlaskConical },
  { to: "/admin/prompts", label: "Prompts", Icon: ScrollText },
];

interface SidebarContentProps {
  isMobile?: boolean;
  expanded: boolean;
  setExpanded: (fn: (v: boolean) => boolean) => void;
  pathname: string;
  navigate: (opts: { to: string }) => void;
  navItems: Array<NavItem>;
  bottomItems: Array<NavItem>;
  isAdmin: boolean;
}

function SidebarContent({
  isMobile = false,
  expanded,
  setExpanded,
  pathname,
  navigate,
  navItems,
  bottomItems,
  isAdmin,
}: SidebarContentProps) {
  return (
    <div className="flex flex-col h-full justify-between py-6">
      <div className="px-3 flex flex-col gap-3 pb-4">
        <div className="h-12 rounded-[32px] flex items-center gap-6 px-3 bg-transparent flex-shrink-0">
          <img
            src="/neovita_logo_small.png"
            alt="Neovita"
            className="h-6 w-auto flex-shrink-0"
            style={{ minWidth: "24px", width: "24px" }}
          />
          <AnimatePresence initial={false}>
            {(expanded || isMobile) && (
              <motion.span
                initial={{ opacity: 0, width: 0, marginLeft: 0 }}
                animate={{ opacity: 1, width: "auto", marginLeft: 12 }}
                exit={{ opacity: 0, width: 0, marginLeft: 0 }}
                transition={{ duration: 0.25, ease: "easeInOut" }}
                className="text-base font-semibold tracking-tight text-[color:var(--nv-indigo)] whitespace-nowrap overflow-hidden"
              >
                neovita
              </motion.span>
            )}
          </AnimatePresence>
        </div>
      </div>

      <nav className="flex-1 flex flex-col gap-6 pt-6 px-3">
        {navItems.map(({ to, label, icon }) => {
          const isActive = pathname === to || pathname.startsWith(to + "/");
          const isChatIcon = icon === "/ai-bubble-white.svg";
          const iconSrc = isChatIcon
            ? isActive
              ? "/ai-bubble-white.svg"
              : "/ai-bubble-purple.svg"
            : icon;
          const iconFilter = isChatIcon
            ? ""
            : isActive
              ? "brightness-0 invert"
              : "";
          return (
            <button
              key={to}
              type="button"
              onClick={() => {
                navigate({ to });
              }}
              className={
                `w-full h-12 rounded-[32px] flex items-center gap-6 px-3 transition-colors duration-200 ` +
                (isActive
                  ? "bg-[var(--nv-royal-purple)]"
                  : "bg-[var(--nv-lilac-white)] ring-1 ring-[#b8b8b8]/60 hover:bg-[var(--nv-pale-lavender)] hover:ring-[var(--nv-royal-purple)]/30")
              }
            >
              <img
                src={iconSrc}
                alt=""
                className={`w-6 h-6 flex-shrink-0 ${iconFilter}`}
              />
              <AnimatePresence initial={false}>
                {(expanded || isMobile) && (
                  <motion.span
                    initial={{ opacity: 0, width: 0, marginLeft: 0 }}
                    animate={{ opacity: 1, width: "auto", marginLeft: 12 }}
                    exit={{ opacity: 0, width: 0, marginLeft: 0 }}
                    transition={{ duration: 0.25, ease: "easeInOut" }}
                    className={`text-sm font-medium whitespace-nowrap overflow-hidden ${isActive ? "text-white" : "text-[color:var(--nv-royal-purple)]"}`}
                  >
                    {label}
                  </motion.span>
                )}
              </AnimatePresence>
            </button>
          );
        })}
      </nav>

      {isAdmin && (
        <div className="flex flex-col gap-3 px-3 pt-6">
          <div className="flex items-center gap-2 px-3 h-6">
            <Shield className="w-4 h-4 flex-shrink-0 text-[color:var(--nv-royal-purple)]/50" />
            <AnimatePresence initial={false}>
              {(expanded || isMobile) && (
                <motion.span
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: "auto" }}
                  exit={{ opacity: 0, width: 0 }}
                  transition={{ duration: 0.25, ease: "easeInOut" }}
                  className="text-xs font-semibold uppercase tracking-wider text-[color:var(--nv-royal-purple)]/50 whitespace-nowrap overflow-hidden"
                >
                  Admin
                </motion.span>
              )}
            </AnimatePresence>
          </div>
          {adminNavItems.map(({ to, label, Icon }) => {
            const isActive = pathname === to || pathname.startsWith(to + "/");
            return (
              <button
                key={to}
                type="button"
                onClick={() => navigate({ to })}
                className={
                  `w-full h-12 rounded-[32px] flex items-center gap-6 px-3 transition-colors duration-200 ` +
                  (isActive
                    ? "bg-[var(--nv-royal-purple)]"
                    : "bg-[var(--nv-lilac-white)] ring-1 ring-[#b8b8b8]/60 hover:bg-[var(--nv-pale-lavender)] hover:ring-[var(--nv-royal-purple)]/30")
                }
              >
                <Icon
                  className={`w-6 h-6 flex-shrink-0 ${isActive ? "text-white" : "text-[color:var(--nv-royal-purple)]"}`}
                />
                <AnimatePresence initial={false}>
                  {(expanded || isMobile) && (
                    <motion.span
                      initial={{ opacity: 0, width: 0, marginLeft: 0 }}
                      animate={{ opacity: 1, width: "auto", marginLeft: 12 }}
                      exit={{ opacity: 0, width: 0, marginLeft: 0 }}
                      transition={{ duration: 0.25, ease: "easeInOut" }}
                      className={`text-sm font-medium whitespace-nowrap overflow-hidden ${isActive ? "text-white" : "text-[color:var(--nv-royal-purple)]"}`}
                    >
                      {label}
                    </motion.span>
                  )}
                </AnimatePresence>
              </button>
            );
          })}
        </div>
      )}

      <div className="flex flex-col gap-3 px-3 pt-6 pb-1">
        {!isMobile && (
          <button
            type="button"
            className="w-full h-12 rounded-[32px] flex items-center gap-6 px-3 bg-[var(--nv-lilac-white)] ring-1 ring-[#b8b8b8]/60 hover:bg-[var(--nv-pale-lavender)] hover:ring-[var(--nv-royal-purple)]/30 transition-colors duration-200"
            onClick={() => setExpanded((v) => !v)}
            aria-label={expanded ? "Collapse sidebar" : "Expand sidebar"}
          >
            <img
              src={toggleIcon}
              alt=""
              className="h-6 w-6 object-contain flex-shrink-0 transition-transform ease-in-out"
              style={{
                transform: expanded ? "scaleX(-1)" : "scaleX(1)",
                transitionDuration: "250ms",
              }}
            />
            <AnimatePresence initial={false}>
              {expanded && (
                <motion.span
                  initial={{ opacity: 0, width: 0, marginLeft: 0 }}
                  animate={{ opacity: 1, width: "auto", marginLeft: 12 }}
                  exit={{ opacity: 0, width: 0, marginLeft: 0 }}
                  transition={{ duration: 0.25, ease: "easeInOut" }}
                  className="text-sm font-medium text-[color:var(--nv-royal-purple)] whitespace-nowrap overflow-hidden"
                >
                  Collapse
                </motion.span>
              )}
            </AnimatePresence>
          </button>
        )}
        {bottomItems.map(({ to, label, icon }) => {
          const isActive = pathname === to || pathname.startsWith(to + "/");
          return (
            <button
              key={to}
              type="button"
              onClick={() => {
                navigate({ to });
              }}
              className={
                `w-full h-12 rounded-[32px] flex items-center gap-6 px-3 transition-colors duration-200 ` +
                (isActive
                  ? "bg-[var(--nv-royal-purple)]"
                  : "bg-[var(--nv-lilac-white)] ring-1 ring-[#b8b8b8]/60 hover:bg-[var(--nv-pale-lavender)] hover:ring-[var(--nv-royal-purple)]/30")
              }
            >
              <img
                src={icon}
                alt=""
                className={`w-6 h-6 flex-shrink-0 ${isActive ? "brightness-0 invert" : ""}`}
              />
              <AnimatePresence initial={false}>
                {(expanded || isMobile) && (
                  <motion.span
                    initial={{ opacity: 0, width: 0, marginLeft: 0 }}
                    animate={{ opacity: 1, width: "auto", marginLeft: 12 }}
                    exit={{ opacity: 0, width: 0, marginLeft: 0 }}
                    transition={{ duration: 0.25, ease: "easeInOut" }}
                    className={`text-sm font-medium whitespace-nowrap overflow-hidden ${isActive ? "text-white" : "text-[color:var(--nv-royal-purple)]"}`}
                  >
                    {label}
                  </motion.span>
                )}
              </AnimatePresence>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default function AuthLayout({ children }: { children?: ReactNode }) {
  const routerState = useRouterState();
  const pathname = routerState.location.pathname;
  const navigate = useNavigate();
  const { isAdmin } = useProfile();

  const navItems: Array<NavItem> = [
    { to: "/chat", label: "AI Coach", icon: "/ai-bubble-white.svg" },
    {
      to: "/identities",
      label: "Identities",
      icon: "/users-round.svg",
    },
    { to: "/iams", label: "I Am's", icon: "/list.svg" },
    { to: "/studio", label: "Studio", icon: "/brush.svg" },
  ];

  const bottomItems: Array<NavItem> = [
    { to: "/account", label: "Account", icon: "/baseline-settings.svg" },
  ];

  const [expanded, setExpanded] = useState(false);

  return (
    <div className="w-full h-screen bg-[var(--nv-lilac-white)] text-foreground flex flex-col sm:flex-row p-3">
      {/* Mobile header only visible on mobile - fixed at top */}
      <MobileAuthHeader />

      {/* Container with max-width for sidebar + main content */}
      <div className="flex-1 flex flex-col sm:flex-row gap-3 max-w-[1700px] mx-auto w-full sm:pt-0 pt-24 pb-24 sm:pb-0">
        {/* Sidebar rail per Figma with expandable variant */}
        <aside className="hidden sm:flex shrink-0 h-full sticky top-0 items-center justify-center">
          <motion.div
            initial={false}
            animate={{ width: expanded ? 240 : 100 }}
            transition={{ type: "tween", duration: 0.25, ease: "easeInOut" }}
            className="h-full rounded-2xl flex items-stretch justify-center"
            style={{ willChange: "width" }}
          >
            <motion.div
              initial={false}
              animate={{ width: expanded ? 212 : 72 }}
              transition={{ type: "tween", duration: 0.25, ease: "easeInOut" }}
              className="bg-white rounded-2xl overflow-hidden"
              style={{ willChange: "width" }}
            >
              <SidebarContent
                isMobile={false}
                expanded={expanded}
                setExpanded={setExpanded}
                pathname={pathname}
                navigate={navigate}
                navItems={navItems}
                bottomItems={bottomItems}
                isAdmin={isAdmin ?? false}
              />
            </motion.div>
          </motion.div>
        </aside>

        {/* Main content - scrollable on mobile between header and footer */}
        <div className="flex-1 min-w-0 h-full sm:h-full flex flex-col bg-white rounded-2xl overflow-hidden">
          <ImpersonationBanner />
          <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
            {children}
          </main>
        </div>
      </div>

      {/* Mobile footer only visible on mobile - fixed at bottom */}
      <MobileAuthFooter />
    </div>
  );
}
