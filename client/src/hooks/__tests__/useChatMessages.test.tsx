/**
 * Tests for useChatMessages.
 *
 * PR 15 (Coaching Phase Videos): asserts that `on_break` from the coach
 * response is mirrored into the `coachState` query cache in `onSuccess`,
 * so the composer flips this paint instead of waiting for the
 * `invalidateQueries` refetch to round-trip.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";
import { useChatMessages } from "@/hooks/use-chat-messages";
import { createQueryWrapper } from "@/tests/query-wrapper";
import { CoachingPhase } from "@/enums/coachingPhase";
import type { CoachResponse } from "@/types/coachResponse";
import type { CoachState } from "@/types/coachState";

vi.mock("@/api/user", () => ({
  fetchChatMessages: vi.fn().mockResolvedValue([]),
  resetChatMessages: vi.fn(),
}));

vi.mock("@/api/testScenarioUser", () => ({
  fetchTestScenarioChatMessages: vi.fn().mockResolvedValue([]),
}));

vi.mock("@/api/coach", () => ({
  apiClient: {
    sendMessage: vi.fn(),
    sendTestScenarioMessage: vi.fn(),
  },
}));

vi.mock("@/context/UserTargetContext", () => ({
  useUserTarget: vi.fn().mockReturnValue({
    isImpersonating: false,
    targetUserId: null,
    scenarioId: null,
    queryKeyPrefix: ["user"],
  }),
}));

import { apiClient } from "@/api/coach";

const baseCoachState: CoachState = {
  id: "cs-1",
  user: "user-1",
  current_phase: CoachingPhase.INTRODUCTION,
  who_you_are: null,
  who_you_want_to_be: null,
  asked_questions: null,
  updated_at: "2025-01-01",
  on_break: false,
};

describe("useChatMessages — on_break cache mirror (PR 15)", () => {
  beforeEach(() => {
    vi.mocked(apiClient.sendMessage).mockReset();
  });

  it("mirrors on_break:true from the coach response into the coachState cache", async () => {
    const response: CoachResponse = {
      message: "",
      on_break: true,
    };
    vi.mocked(apiClient.sendMessage).mockResolvedValue(response);

    const { queryClient, wrapper } = createQueryWrapper();
    // Seed the coachState cache as if the initial fetch had landed.
    queryClient.setQueryData(["user", "coachState"], baseCoachState);

    const { result } = renderHook(() => useChatMessages(), { wrapper });

    await act(async () => {
      await result.current.updateChatMessages({ message: "" });
    });

    await waitFor(() => {
      const cached = queryClient.getQueryData<CoachState>([
        "user",
        "coachState",
      ]);
      expect(cached?.on_break).toBe(true);
    });
  });

  it("mirrors on_break:false from the coach response into the coachState cache", async () => {
    const response: CoachResponse = {
      message: "",
      on_break: false,
    };
    vi.mocked(apiClient.sendMessage).mockResolvedValue(response);

    const { queryClient, wrapper } = createQueryWrapper();
    queryClient.setQueryData(["user", "coachState"], {
      ...baseCoachState,
      on_break: true,
    });

    const { result } = renderHook(() => useChatMessages(), { wrapper });

    await act(async () => {
      await result.current.updateChatMessages({ message: "I'm ready" });
    });

    await waitFor(() => {
      const cached = queryClient.getQueryData<CoachState>([
        "user",
        "coachState",
      ]);
      expect(cached?.on_break).toBe(false);
    });
  });

  it("leaves coachState untouched when on_break is omitted from the response", async () => {
    const response: CoachResponse = {
      message: "Normal turn, no break state change.",
    };
    vi.mocked(apiClient.sendMessage).mockResolvedValue(response);

    const { queryClient, wrapper } = createQueryWrapper();
    queryClient.setQueryData(["user", "coachState"], {
      ...baseCoachState,
      on_break: true,
    });

    const { result } = renderHook(() => useChatMessages(), { wrapper });

    await act(async () => {
      await result.current.updateChatMessages({ message: "Hello" });
    });

    // The pre-mutation on_break value should still be present (the
    // invalidation will refetch separately — we're asserting the mirror
    // doesn't clobber on missing field).
    const cached = queryClient.getQueryData<CoachState>([
      "user",
      "coachState",
    ]);
    expect(cached?.on_break).toBe(true);
  });
});
