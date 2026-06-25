import { useMeditations } from "@/hooks/use-meditations";
import AdminMeditations from "@/pages/admin-meditations/AdminMeditations";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";

/**
 * /admin/meditations — gated behind the MEDITATIONS_ENABLED backend flag.
 *
 * The parent /admin route already restricts to admins; this additionally
 * hides the feature until the backend flag is on. When the flag is off the
 * route redirects to /chat so the half-built feature is invisible in prod.
 */
export const Route = createFileRoute("/_authenticated/admin/meditations")({
	component: MeditationsRoute,
});

function MeditationsRoute() {
	const { enabled, isLoading } = useMeditations();
	const navigate = useNavigate();

	useEffect(() => {
		if (!isLoading && !enabled) navigate({ to: "/chat" });
	}, [enabled, isLoading, navigate]);

	if (isLoading || !enabled) return null;
	return <AdminMeditations />;
}
