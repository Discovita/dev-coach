import { createFileRoute } from "@tanstack/react-router";
import Test from "@/pages/test/Test";

export const Route = createFileRoute("/_authenticated/admin/test")({
  component: Test,
});
