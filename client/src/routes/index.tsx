import LandingPage from "@/pages/landing/LandingPage";
import { createFileRoute } from "@tanstack/react-router";

/**
 * Root route (/) - Public landing page
 * Renders the new Figma Option 3 landing page design
 * Uses PublicLayout for consistent navbar and footer
 */
export const Route = createFileRoute("/")({
	component: function RootLandingPage() {
		return <LandingPage />;
	},
});
