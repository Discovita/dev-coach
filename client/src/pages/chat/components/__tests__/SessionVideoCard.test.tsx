/**
 * Tests for SessionVideoCard + SessionVideoModal — the Coaching Phase
 * Videos thin card + modal player (PR 16 shell).
 *
 * Scope: visual shell only. PR 16 deliberately does NOT render a Continue
 * button, threshold-gate anything, or dispatch any backend actions on
 * close — those are PR 17's responsibility. The negative tests in this
 * file lock that split.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ActionType } from "@/enums/actionType";
import { CoachingPhase } from "@/enums/coachingPhase";
import { ComponentType } from "@/enums/componentType";
import { SessionVideoCard } from "@/pages/chat/components/coach-message-with-component/SessionVideoCard";
import { createQueryWrapper } from "@/tests/query-wrapper";
import type { CoachState } from "@/types/coachState";
import type { ComponentConfig } from "@/types/componentConfig";

vi.mock("@/hooks/use-coach-state", () => ({
  useCoachState: vi.fn(),
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
  shown_videos: [],
};

function mockCoachState(state: Partial<CoachState> = {}) {
  vi.mocked(useCoachState).mockReturnValue({
    coachState: { ...baseCoachState, ...state },
    isLoading: false,
    isError: false,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    refetchCoachState: vi.fn() as any,
  });
}

function buildConfig(overrides: Partial<ComponentConfig> = {}): ComponentConfig {
  return {
    component_type: ComponentType.SESSION_VIDEO,
    video_key: "welcome_session_intro",
    video_name: "Welcome",
    video_url:
      "https://discovita-dev-coach-staging.s3.amazonaws.com/media/session-videos/01-welcome-session-intro.mov",
    buttons: [
      {
        label: "Continue",
        actions: [
          {
            action: ActionType.ACKNOWLEDGE_SESSION_VIDEO,
            params: { video_key: "welcome_session_intro" },
          },
        ],
      },
    ],
    ...overrides,
  };
}

function renderCard(
  config: ComponentConfig = buildConfig(),
  coachMessage: React.ReactNode = null,
  onSendUserMessageToCoach = vi.fn()
) {
  const { wrapper: Wrapper } = createQueryWrapper();
  const result = render(
    <Wrapper>
      <SessionVideoCard
        coachMessage={coachMessage}
        config={config}
        onSendUserMessageToCoach={onSendUserMessageToCoach}
      />
    </Wrapper>
  );
  return { ...result, onSendUserMessageToCoach };
}

describe("SessionVideoCard — shell (PR 16)", () => {
  beforeEach(() => {
    vi.mocked(useCoachState).mockReset();
    mockCoachState();
  });

  // --- Card surface --------------------------------------------------

  it("renders the video name from component_config.video_name", () => {
    renderCard(buildConfig({ video_name: "Brainstorming Intro" }));
    expect(screen.getByText("Brainstorming Intro")).toBeInTheDocument();
  });

  it("renders a Watch button when video_key is NOT in shown_videos", () => {
    mockCoachState({ shown_videos: ["some_other_video"] });
    renderCard();
    expect(
      screen.getByRole("button", { name: "Watch" })
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Watch Again" })
    ).not.toBeInTheDocument();
  });

  it("renders Watch Again when video_key IS in shown_videos", () => {
    mockCoachState({ shown_videos: ["welcome_session_intro"] });
    renderCard();
    expect(
      screen.getByRole("button", { name: "Watch Again" })
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Watch" })
    ).not.toBeInTheDocument();
  });

  it("treats undefined shown_videos as 'never acked' (Watch label)", () => {
    // Graceful for older backend responses that omit the field.
    mockCoachState({ shown_videos: undefined });
    renderCard();
    expect(
      screen.getByRole("button", { name: "Watch" })
    ).toBeInTheDocument();
  });

  // --- Modal lifecycle ------------------------------------------------

  it("opens the modal on Watch click and renders a <video> with the right src", () => {
    renderCard();
    expect(screen.queryByTestId("session-video-modal")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Watch" }));

    expect(screen.getByTestId("session-video-modal")).toBeInTheDocument();
    const videoEl = screen.getByTestId("session-video-element") as HTMLVideoElement;
    expect(videoEl).toBeInTheDocument();
    expect(videoEl.getAttribute("src")).toBe(
      "https://discovita-dev-coach-staging.s3.amazonaws.com/media/session-videos/01-welcome-session-intro.mov"
    );
  });

  it("closes the modal on Escape", () => {
    renderCard();
    fireEvent.click(screen.getByRole("button", { name: "Watch" }));
    expect(screen.getByTestId("session-video-modal")).toBeInTheDocument();

    fireEvent.keyDown(document.body, { key: "Escape" });

    expect(screen.queryByTestId("session-video-modal")).not.toBeInTheDocument();
  });

  it("renders a Continue button inside the modal for unacked videos (PR 17)", () => {
    renderCard();
    fireEvent.click(screen.getByRole("button", { name: "Watch" }));

    expect(screen.getByTestId("session-video-continue")).toBeInTheDocument();
  });

  it("hides the Continue button on Watch Again (acked) modal", () => {
    mockCoachState({ shown_videos: ["welcome_session_intro"] });
    renderCard();
    fireEvent.click(screen.getByRole("button", { name: "Watch Again" }));

    expect(
      screen.queryByTestId("session-video-continue")
    ).not.toBeInTheDocument();
  });

  // --- Coach text passthrough ----------------------------------------

  it("renders the coach message text above the card when content is non-empty", () => {
    // Mirror what ChatMessages.tsx actually passes — a MarkdownRenderer-
    // shaped element with a `content` prop. The card's
    // `extractContentString` helper inspects that prop to decide whether
    // to render the text bubble.
    const Fake = ({ content }: { content: string }) => (
      <div data-testid="coach-text">{content}</div>
    );
    renderCard(buildConfig(), <Fake content="Let's move to brainstorming." />);
    expect(
      screen.getByText("Let's move to brainstorming.")
    ).toBeInTheDocument();
  });

  it("suppresses the text bubble when coachMessage's content prop is empty (welcome card)", () => {
    const Fake = ({ content }: { content: string }) => (
      <div data-testid="coach-text">{content || "should-not-render"}</div>
    );
    renderCard(buildConfig(), <Fake content="" />);
    // Element exists in the React tree only if the card chose to render
    // the text bubble — which it shouldn't when content is empty.
    expect(screen.queryByTestId("coach-text")).not.toBeInTheDocument();
  });
});
