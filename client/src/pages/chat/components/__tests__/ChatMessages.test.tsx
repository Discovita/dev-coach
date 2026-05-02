import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { ChatMessages } from "@/pages/chat/components/ChatMessages";
import type { Message } from "@/types/message";
import { createRef } from "react";

vi.mock("@/utils/MarkdownRenderer", () => ({
  default: ({ content }: { content: string }) => <span data-testid="markdown">{content}</span>,
}));

vi.mock("@/pages/chat/components/CoachMessage", () => ({
  CoachMessage: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="coach-message">{children}</div>
  ),
}));

vi.mock("@/pages/chat/components/UserMessage", () => ({
  UserMessage: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="user-message">{children}</div>
  ),
}));

vi.mock("@/pages/chat/components/LoadingBubbles", () => ({
  LoadingBubbles: () => <div data-testid="loading-bubbles" />,
}));

vi.mock(
  "@/pages/chat/components/coach-message-with-component/CoachMessageWithComponent",
  () => ({
    CoachMessageWithComponent: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="coach-with-component">{children}</div>
    ),
  })
);

const mockOnSend = vi.fn();

function renderChatMessages(
  messages: Message[],
  options: { isProcessingMessage?: boolean; componentConfig?: null } = {}
) {
  const messagesEndRef = createRef<HTMLDivElement>();
  return render(
    <ChatMessages
      messages={messages}
      isProcessingMessage={options.isProcessingMessage ?? false}
      messagesEndRef={messagesEndRef}
      componentConfig={options.componentConfig ?? null}
      onSendUserMessageToCoach={mockOnSend}
    />
  );
}

describe("ChatMessages", () => {
  it("renders user messages with UserMessage component", () => {
    renderChatMessages([
      { role: "user", content: "Hello coach", timestamp: "2025-01-01T00:00:00Z" },
    ]);
    expect(screen.getByTestId("user-message")).toBeInTheDocument();
    expect(screen.getByText("Hello coach")).toBeInTheDocument();
  });

  it("renders coach messages with CoachMessage component", () => {
    renderChatMessages([
      { role: "coach", content: "Welcome!", timestamp: "2025-01-01T00:00:00Z" },
    ]);
    expect(screen.getByTestId("coach-message")).toBeInTheDocument();
    expect(screen.getByText("Welcome!")).toBeInTheDocument();
  });

  it("renders multiple messages in order", () => {
    renderChatMessages([
      { role: "user", content: "Hi", timestamp: "2025-01-01T00:00:00Z" },
      { role: "coach", content: "Hello!", timestamp: "2025-01-01T00:00:01Z" },
      { role: "user", content: "How are you?", timestamp: "2025-01-01T00:00:02Z" },
    ]);
    expect(screen.getAllByTestId("user-message")).toHaveLength(2);
    expect(screen.getAllByTestId("coach-message")).toHaveLength(1);
  });

  it("shows loading bubbles when processing", () => {
    renderChatMessages(
      [{ role: "user", content: "Hello", timestamp: "2025-01-01T00:00:00Z" }],
      { isProcessingMessage: true }
    );
    expect(screen.getByTestId("loading-bubbles")).toBeInTheDocument();
  });

  it("does not show loading bubbles when not processing", () => {
    renderChatMessages(
      [{ role: "user", content: "Hello", timestamp: "2025-01-01T00:00:00Z" }],
      { isProcessingMessage: false }
    );
    expect(screen.queryByTestId("loading-bubbles")).not.toBeInTheDocument();
  });

  it("renders unknown role messages with fallback styling", () => {
    renderChatMessages([
      { role: "system", content: "System message", timestamp: "2025-01-01T00:00:00Z" },
    ]);
    expect(screen.getByText("System message")).toBeInTheDocument();
    expect(screen.queryByTestId("coach-message")).not.toBeInTheDocument();
    expect(screen.queryByTestId("user-message")).not.toBeInTheDocument();
  });

  it("renders empty message list without crashing", () => {
    renderChatMessages([]);
    expect(screen.queryByTestId("coach-message")).not.toBeInTheDocument();
    expect(screen.queryByTestId("user-message")).not.toBeInTheDocument();
  });
});
