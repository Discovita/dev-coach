import { createFileRoute } from "@tanstack/react-router";
import Onboarding from "@/pages/onboarding/Onboarding.tsx";

/**
 * /onboarding — guided post-verification setup (appearance + reference photos)
 * before a newly verified user is dropped into the coach chat.
 */
export const Route = createFileRoute("/onboarding/")({
  component: Onboarding,
});
