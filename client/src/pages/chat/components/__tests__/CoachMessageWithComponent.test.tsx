import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { CoachMessageWithComponent } from "@/pages/chat/components/coach-message-with-component/CoachMessageWithComponent";
import { ComponentType } from "@/enums/componentType";
import type { ComponentConfig } from "@/types/componentConfig";

vi.mock(
  "@/pages/chat/components/coach-message-with-component/IntroCannedResponseComponent",
  () => ({
    IntroCannedResponseComponent: ({ coachMessage }: { coachMessage: React.ReactNode }) => (
      <div data-testid="intro-canned">{coachMessage}</div>
    ),
  })
);
vi.mock(
  "@/pages/chat/components/coach-message-with-component/CombineIdentitiesConfirmation",
  () => ({
    CombineIdentitiesConfirmation: ({ coachMessage }: { coachMessage: React.ReactNode }) => (
      <div data-testid="combine-identities">{coachMessage}</div>
    ),
  })
);
vi.mock(
  "@/pages/chat/components/coach-message-with-component/NestIdentitiesConfirmation",
  () => ({
    NestIdentitiesConfirmation: ({ coachMessage }: { coachMessage: React.ReactNode }) => (
      <div data-testid="nest-identities">{coachMessage}</div>
    ),
  })
);
vi.mock(
  "@/pages/chat/components/coach-message-with-component/ArchiveIdentityConfirmation",
  () => ({
    ArchiveIdentityConfirmation: ({ coachMessage }: { coachMessage: React.ReactNode }) => (
      <div data-testid="archive-identity">{coachMessage}</div>
    ),
  })
);
vi.mock(
  "@/pages/chat/components/coach-message-with-component/SuggestIAmStatementComponent",
  () => ({
    SuggestIAmStatementComponent: ({ coachMessage }: { coachMessage: React.ReactNode }) => (
      <div data-testid="suggest-iam">{coachMessage}</div>
    ),
  })
);
vi.mock(
  "@/pages/chat/components/coach-message-with-component/IAmStatementsSummaryComponent",
  () => ({
    IAmStatementsSummaryComponent: ({ coachMessage }: { coachMessage: React.ReactNode }) => (
      <div data-testid="iam-summary">{coachMessage}</div>
    ),
  })
);

const mockOnSend = vi.fn();

function renderWithConfig(componentType: ComponentType) {
  const config: ComponentConfig = {
    component_type: componentType,
    buttons: [{ label: "Test" }],
  };

  return render(
    <CoachMessageWithComponent
      componentConfig={config}
      onSendUserMessageToCoach={mockOnSend}
      disabled={false}
    >
      <span>Coach message text</span>
    </CoachMessageWithComponent>
  );
}

describe("CoachMessageWithComponent", () => {
  it("renders IntroCannedResponseComponent for INTRO_CANNED_RESPONSE", () => {
    renderWithConfig(ComponentType.INTRO_CANNED_RESPONSE);
    expect(screen.getByTestId("intro-canned")).toBeInTheDocument();
  });

  it("renders CombineIdentitiesConfirmation for COMBINE_IDENTITIES", () => {
    renderWithConfig(ComponentType.COMBINE_IDENTITIES);
    expect(screen.getByTestId("combine-identities")).toBeInTheDocument();
  });

  it("renders NestIdentitiesConfirmation for NEST_IDENTITIES", () => {
    renderWithConfig(ComponentType.NEST_IDENTITIES);
    expect(screen.getByTestId("nest-identities")).toBeInTheDocument();
  });

  it("renders ArchiveIdentityConfirmation for ARCHIVE_IDENTITY", () => {
    renderWithConfig(ComponentType.ARCHIVE_IDENTITY);
    expect(screen.getByTestId("archive-identity")).toBeInTheDocument();
  });

  it("renders SuggestIAmStatementComponent for SUGGEST_I_AM_STATEMENT", () => {
    renderWithConfig(ComponentType.SUGGEST_I_AM_STATEMENT);
    expect(screen.getByTestId("suggest-iam")).toBeInTheDocument();
  });

  it("renders IAmStatementsSummaryComponent for I_AM_STATEMENTS_SUMMARY", () => {
    renderWithConfig(ComponentType.I_AM_STATEMENTS_SUMMARY);
    expect(screen.getByTestId("iam-summary")).toBeInTheDocument();
  });

  it("renders children as fallback for unknown component type", () => {
    const config: ComponentConfig = {
      component_type: "totally_unknown" as ComponentType,
    };
    render(
      <CoachMessageWithComponent
        componentConfig={config}
        onSendUserMessageToCoach={mockOnSend}
        disabled={false}
      >
        <span>Fallback content</span>
      </CoachMessageWithComponent>
    );
    expect(screen.getByText("Fallback content")).toBeInTheDocument();
  });
});
