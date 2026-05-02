import { createFileRoute } from "@tanstack/react-router";
import Signup from "@/pages/signup/Signup.tsx";

/**
 * /signup index page under pathless _public layout.
 */
export const Route = createFileRoute("/signup/")({
  component: Signup,
});
