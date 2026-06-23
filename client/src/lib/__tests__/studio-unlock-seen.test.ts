import { describe, it, expect, beforeEach } from "vitest";
import {
  hasSeenStudioUnlock,
  markStudioUnlockSeen,
} from "@/lib/studio-unlock-seen";

describe("studio-unlock-seen", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("reports not-seen before it is marked", () => {
    expect(hasSeenStudioUnlock("user-1")).toBe(false);
  });

  it("reports seen after marking, scoped per user", () => {
    markStudioUnlockSeen("user-1");
    expect(hasSeenStudioUnlock("user-1")).toBe(true);
    // A different user has its own flag.
    expect(hasSeenStudioUnlock("user-2")).toBe(false);
  });

  it("treats a null user id as already-seen (never shows without identity)", () => {
    expect(hasSeenStudioUnlock(null)).toBe(true);
    // marking null is a no-op and must not throw
    expect(() => markStudioUnlockSeen(null)).not.toThrow();
  });
});
