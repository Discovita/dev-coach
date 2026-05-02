import { createFileRoute } from "@tanstack/react-router";
import Chat from "@/pages/chat/Chat.tsx";

/**
 * /chat index page under pathless _authenticated layout.
 */
export const Route = createFileRoute("/_authenticated/chat/")({
  component: Chat,
});
