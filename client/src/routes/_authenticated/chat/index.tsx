import Chat from "@/pages/chat/Chat.tsx";
import { createFileRoute } from "@tanstack/react-router";

/**
 * /chat index page under pathless _authenticated layout.
 */
export const Route = createFileRoute("/_authenticated/chat/")({
	component: Chat,
});
