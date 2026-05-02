import { createFileRoute } from "@tanstack/react-router";
import Prompts from "@/pages/prompts/Prompts";

export const Route = createFileRoute("/_authenticated/admin/prompts")({
  component: Prompts,
});
