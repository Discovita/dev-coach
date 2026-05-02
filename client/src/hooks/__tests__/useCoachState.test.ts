import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useCoachState } from "@/hooks/use-coach-state";
import { createQueryWrapper } from "@/tests/query-wrapper";
import { CoachingPhase } from "@/enums/coachingPhase";

vi.mock("@/api/user", () => ({
  fetchCoachState: vi.fn(),
}));

vi.mock("@/api/testScenarioUser", () => ({
  fetchTestScenarioUserCoachState: vi.fn(),
}));

vi.mock("@/context/UserTargetContext", () => ({
  useUserTarget: vi.fn().mockReturnValue({
    isImpersonating: false,
    targetUserId: null,
    scenarioId: null,
    queryKeyPrefix: ["user"],
  }),
}));

import { fetchCoachState } from "@/api/user";
import { useUserTarget } from "@/context/UserTargetContext";
import { fetchTestScenarioUserCoachState } from "@/api/testScenarioUser";

const mockCoachState = {
  id: "cs-1",
  user: "user-1",
  current_phase: CoachingPhase.INTRODUCTION,
  who_you_are: null,
  who_you_want_to_be: null,
  asked_questions: null,
  updated_at: "2025-01-01",
};

describe("useCoachState", () => {
  beforeEach(() => {
    vi.mocked(fetchCoachState).mockReset();
    vi.mocked(fetchTestScenarioUserCoachState).mockReset();
    vi.mocked(useUserTarget).mockReturnValue({
      isImpersonating: false,
      targetUserId: null,
      scenarioId: null,
      queryKeyPrefix: ["user"],
    });
  });

  it("fetches coach state for the logged-in user", async () => {
    vi.mocked(fetchCoachState).mockResolvedValue(mockCoachState);
    const { wrapper } = createQueryWrapper();

    const { result } = renderHook(() => useCoachState(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.coachState).toEqual(mockCoachState);
  });

  it("fetches from admin endpoint when impersonating", async () => {
    vi.mocked(useUserTarget).mockReturnValue({
      isImpersonating: true,
      targetUserId: "target-1",
      scenarioId: "s-1",
      queryKeyPrefix: ["testScenarioUser", "target-1"],
    });
    vi.mocked(fetchTestScenarioUserCoachState).mockResolvedValue(mockCoachState);
    const { wrapper } = createQueryWrapper();

    const { result } = renderHook(() => useCoachState(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(fetchTestScenarioUserCoachState).toHaveBeenCalledWith("target-1");
    expect(fetchCoachState).not.toHaveBeenCalled();
  });

  it("handles fetch errors", async () => {
    vi.mocked(fetchCoachState).mockRejectedValue(new Error("fail"));
    const { wrapper } = createQueryWrapper();

    const { result } = renderHook(() => useCoachState(), { wrapper });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.coachState).toBeUndefined();
  });
});
