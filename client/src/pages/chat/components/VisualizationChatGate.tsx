import { useNavigate } from "@tanstack/react-router";
import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * VisualizationChatGate
 *
 * Replaces the chat composer once the user reaches the identity
 * visualization phase. The coach does nothing in this phase (the backend
 * skips the LLM), so there is nothing to chat about — the user's remaining
 * work happens in the Studio. This panel makes that explicit and sends them
 * there.
 *
 * Rendered by ChatInterface in place of <ChatControls> when
 * coachState.current_phase === IDENTITY_VISUALIZATION.
 */
export const VisualizationChatGate: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="_VisualizationChatGate bg-gold-200 dark:bg-[#333333] sm:p-4">
      <div className="flex flex-col items-center gap-3 text-center px-4 py-5">
        <p className="text-sm text-neutral-700 dark:text-neutral-200 max-w-md">
          You've finished your coaching sessions. There's nothing more to chat
          about here — head to your Studio to bring your identities to life.
        </p>
        <Button
          type="button"
          onClick={() => navigate({ to: "/studio" })}
          className="gap-2"
        >
          <Sparkles className="w-4 h-4" />
          Go to the Studio
        </Button>
      </div>
    </div>
  );
};
