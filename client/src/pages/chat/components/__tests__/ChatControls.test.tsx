/**
 * Tests for ChatControls — the composer (textarea + send button) that
 * renders at the bottom of the chat page.
 *
 * PR 15 (Coaching Phase Videos): composer disables when
 * `coachState.on_break === true` so the user must click "I'm Ready" on
 * the break card before they can type again. The unacked-SESSION_VIDEO
 * disable clause ships in PR 18.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { ChatControls } from "@/pages/chat/components/ChatControls";
import { createQueryWrapper } from "@/tests/query-wrapper";
import { CoachingPhase } from "@/enums/coachingPhase";
import type { CoachState } from "@/types/coachState";

vi.mock("@/hooks/use-coach-state", () => ({
  useCoachState: vi.fn(),
}));

vi.mock("@/hooks/use-identities", () => ({
  useIdentities: vi.fn().mockReturnValue({ identities: [] }),
}));

// The bulletin components are pure functions of coachState/identities;
// stub them out so this test focuses on the composer disable rule.
vi.mock("@/pages/chat/components/WarmupBulletin", () => ({
  WarmupBulletin: () => null,
}));
vi.mock("@/pages/chat/components/BrainstormingBulletin", () => ({
  BrainstormingBulletin: () => null,
}));
vi.mock("@/pages/chat/components/RefinementBulletin", () => ({
  RefinementBulletin: () => null,
}));
vi.mock("@/pages/chat/components/CommitmentBulletin", () => ({
  CommitmentBulletin: () => null,
}));

import { useCoachState } from "@/hooks/use-coach-state";

const baseCoachState: CoachState = {
  id: "cs-1",
  user: "user-1",
  current_phase: CoachingPhase.INTRODUCTION,
  who_you_are: null,
  who_you_want_to_be: null,
  asked_questions: null,
  updated_at: "2025-01-01",
};

function mockCoachState(coachState: CoachState | undefined) {
  vi.mocked(useCoachState).mockReturnValue({
    coachState,
    isLoading: false,
    isError: false,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    refetchCoachState: vi.fn() as any,
  });
}

function renderControls(processing = false) {
  const { wrapper: Wrapper } = createQueryWrapper();
  return render(
    <Wrapper>
      <ChatControls
        isProcessingMessage={processing}
        onSendMessage={vi.fn()}
      />
    </Wrapper>
  );
}

describe("ChatControls — composer disable rule (PR 15)", () => {
  beforeEach(() => {
    vi.mocked(useCoachState).mockReset();
  });

  it("composer is disabled when on_break is true", () => {
    mockCoachState({ ...baseCoachState, on_break: true });

    renderControls();

    const textarea = screen.getByPlaceholderText(
      "Type your message..."
    ) as HTMLTextAreaElement;
    const sendButton = screen.getByRole("button", { name: "Send" });
    expect(textarea.disabled).toBe(true);
    expect(sendButton).toBeDisabled();
  });

  it("composer is enabled when on_break is false", () => {
    mockCoachState({ ...baseCoachState, on_break: false });

    renderControls();

    const textarea = screen.getByPlaceholderText(
      "Type your message..."
    ) as HTMLTextAreaElement;
    const sendButton = screen.getByRole("button", { name: "Send" });
    expect(textarea.disabled).toBe(false);
    expect(sendButton).not.toBeDisabled();
  });

  it("composer remains enabled when on_break field is missing (graceful)", () => {
    // Older backend responses (pre-PR 9) may omit the field. The composer
    // should default to enabled so we don't lock users out on rollback.
    mockCoachState(baseCoachState);

    renderControls();

    const textarea = screen.getByPlaceholderText(
      "Type your message..."
    ) as HTMLTextAreaElement;
    const sendButton = screen.getByRole("button", { name: "Send" });
    expect(textarea.disabled).toBe(false);
    expect(sendButton).not.toBeDisabled();
  });

  it("composer is disabled when isProcessingMessage is true even with on_break false", () => {
    mockCoachState({ ...baseCoachState, on_break: false });

    renderControls(true);

    const textarea = screen.getByPlaceholderText(
      "Type your message..."
    ) as HTMLTextAreaElement;
    const sendButton = screen.getByRole("button", { name: "Sending..." });
    expect(textarea.disabled).toBe(true);
    expect(sendButton).toBeDisabled();
  });

  it("composer stays enabled when coachState is undefined (initial load)", () => {
    // useCoachState returns undefined during the first paint before the
    // query resolves; the composer should not flicker into a disabled
    // state in that window.
    mockCoachState(undefined);

    renderControls();

    const textarea = screen.getByPlaceholderText(
      "Type your message..."
    ) as HTMLTextAreaElement;
    expect(textarea.disabled).toBe(false);
  });
});
