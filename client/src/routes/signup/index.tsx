import Signup from "@/pages/signup/Signup.tsx";
import { createFileRoute } from "@tanstack/react-router";

/**
 * /signup index page under pathless _public layout.
 */
export const Route = createFileRoute("/signup/")({
	component: Signup,
});
