import { describe, it, expect } from "vitest";
import { isStudioLocked, STUDIO_LOCKED_MESSAGE } from "@/lib/studio-lock";
import { CoachingPhase } from "@/enums/coachingPhase";
import type { CoachState } from "@/types/coachState";

function coachStateInPhase(phase: CoachingPhase): CoachState {
  return {
    id: "cs-1",
    user: "user-1",
    current_phase: phase,
    who_you_are: null,
    who_you_want_to_be: null,
    asked_questions: null,
    updated_at: "2026-01-01T00:00:00Z",
  };
}

describe("isStudioLocked", () => {
  it("is unlocked only in the identity visualization phase", () => {
    expect(
      isStudioLocked(coachStateInPhase(CoachingPhase.IDENTITY_VISUALIZATION)),
    ).toBe(false);
  });

  it("is locked in every other phase", () => {
    const otherPhases = Object.values(CoachingPhase).filter(
      (p) => p !== CoachingPhase.IDENTITY_VISUALIZATION,
    );
    for (const phase of otherPhases) {
      expect(isStudioLocked(coachStateInPhase(phase))).toBe(true);
    }
  });

  it("is locked when the coach state is unknown (still loading / failed)", () => {
    expect(isStudioLocked(undefined)).toBe(true);
  });

  it("exposes a stable user-facing message", () => {
    expect(STUDIO_LOCKED_MESSAGE).toBe("This isn't available yet.");
  });
});
