import Test from "@/pages/test/Test";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated/admin/test")({
	component: Test,
});
