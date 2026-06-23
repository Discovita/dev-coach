import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { toast } from "sonner";
import Studio from "@/pages/studio/Studio";
import { useCoachState } from "@/hooks/use-coach-state";
import { isStudioLocked, STUDIO_LOCKED_MESSAGE } from "@/lib/studio-lock";

/**
 * /studio route under pathless _authenticated layout.
 * Provides identity image generation functionality.
 *
 * Guarded: the Studio is only reachable once the user reaches the identity
 * visualization phase. Direct navigation while locked redirects to /chat
 * (mirrors the admin route guard in _authenticated/admin/route.tsx).
 */
export const Route = createFileRoute("/_authenticated/studio/")({
  component: StudioGuard,
});

function StudioGuard() {
  const { coachState, isLoading } = useCoachState();
  const navigate = useNavigate();
  const locked = isStudioLocked(coachState);

  useEffect(() => {
    if (isLoading) return;
    if (locked) {
      toast(STUDIO_LOCKED_MESSAGE);
      navigate({ to: "/chat" });
    }
  }, [isLoading, locked, navigate]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <span className="text-sm text-muted-foreground">Loading…</span>
      </div>
    );
  }

  if (locked) return null;

  return <Studio />;
}
