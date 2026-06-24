/**
 * PublicLayout
 *
 * Purpose:
 * - Layout for public pages (landing, login, signup) without the authenticated sidebar
 * - Provides clean, minimal layout for marketing and auth pages
 * - Renders child routes via TanStack Router's Outlet
 */

import PublicFooter from "@/components/PublicFooter";
import PublicNavbar from "@/components/PublicNavbar";
import { Outlet } from "@tanstack/react-router";
import type { ReactNode } from "react";

export default function PublicLayout({ children }: { children?: ReactNode }) {
	return (
		<div className="min-h-screen max-h-screen bg-background text-foreground relative overflow-hidden flex flex-col">
			<PublicNavbar />

			{/* Page Content */}
			<main className="flex-1 min-h-0 overflow-y-auto">
				{children ?? <Outlet />}
			</main>

			<div className="mt-auto">
				<PublicFooter />
			</div>
		</div>
	);
}
