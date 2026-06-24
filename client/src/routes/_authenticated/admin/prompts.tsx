import Prompts from "@/pages/prompts/Prompts";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated/admin/prompts")({
	component: Prompts,
});
