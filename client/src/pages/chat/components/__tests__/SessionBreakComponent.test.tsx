/**
 * Tests for SessionBreakComponent (PR 18).
 *
 * The break card uses the canned-response pattern — clicking "I'm Ready"
 * dispatches `{message: button.label, actions: button.actions}` so the
 * label appears as a real user message bubble in chat history (mirrors
 * `IntroCannedResponseComponent`). The server bakes the action chain
 * (`[END_BREAK()]`) into the card in `start_break.py`; the FE forwards
 * verbatim.
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ActionType } from "@/enums/actionType";
import { ComponentType } from "@/enums/componentType";
import { SessionBreakComponent } from "@/pages/chat/components/coach-message-with-component/SessionBreakComponent";
import type { ComponentConfig } from "@/types/componentConfig";

function buildConfig(overrides: Partial<ComponentConfig> = {}): ComponentConfig {
  return {
    component_type: ComponentType.SESSION_BREAK,
    buttons: [
      {
        label: "I'm Ready",
        actions: [{ action: ActionType.END_BREAK, params: {} }],
      },
    ],
    ...overrides,
  };
}

function renderCard(
  config: ComponentConfig = buildConfig(),
  disabled = false,
  coachMessage: React.ReactNode = null,
  onSendUserMessageToCoach = vi.fn()
) {
  const result = render(
    <SessionBreakComponent
      coachMessage={coachMessage}
      config={config}
      onSendUserMessageToCoach={onSendUserMessageToCoach}
      disabled={disabled}
    />
  );
  return { ...result, onSendUserMessageToCoach };
}

describe("SessionBreakComponent (PR 18)", () => {
  it("renders the I'm Ready button using config.buttons[0].label", () => {
    renderCard();
    expect(
      screen.getByRole("button", { name: "I'm Ready" })
    ).toBeInTheDocument();
  });

  it("dispatches {message: 'I'm ready', actions: [END_BREAK()]} on click", () => {
    const { onSendUserMessageToCoach } = renderCard();

    fireEvent.click(screen.getByRole("button", { name: "I'm Ready" }));

    expect(onSendUserMessageToCoach).toHaveBeenCalledTimes(1);
    expect(onSendUserMessageToCoach).toHaveBeenCalledWith({
      message: "I'm Ready",
      actions: [{ action: ActionType.END_BREAK, params: {} }],
    });
  });

  it("sends the button label as a non-null message (canned-response pattern, becomes a user ChatMessage)", () => {
    // The defining difference vs the video Continue button: `message` is
    // a string here, NOT null. That string is what `use-chat-messages.ts
    // onSuccess` reads to insert the optimistic user bubble, which is
    // what makes the label appear in chat history.
    const { onSendUserMessageToCoach } = renderCard();
    fireEvent.click(screen.getByRole("button", { name: "I'm Ready" }));

    const callArg = onSendUserMessageToCoach.mock.calls[0][0];
    expect(callArg.message).not.toBeNull();
    expect(typeof callArg.message).toBe("string");
    expect(callArg.message.length).toBeGreaterThan(0);
  });

  it("forwards button.actions verbatim (server is the source of truth for the action chain)", () => {
    // If the server ever extended the chain (e.g. added a follow-up
    // action), the FE should pick it up automatically without code
    // changes. Lock that here.
    const config = buildConfig({
      buttons: [
        {
          label: "I'm Ready",
          actions: [
            { action: ActionType.END_BREAK, params: {} },
            // hypothetical future server-baked extension
            { action: "log_break_resumed" as ActionType, params: { source: "ui" } },
          ],
        },
      ],
    });
    const { onSendUserMessageToCoach } = renderCard(config);
    fireEvent.click(screen.getByRole("button", { name: "I'm Ready" }));

    expect(onSendUserMessageToCoach.mock.calls[0][0].actions).toEqual([
      { action: ActionType.END_BREAK, params: {} },
      { action: "log_break_resumed", params: { source: "ui" } },
    ]);
  });

  it("respects the disabled prop", () => {
    renderCard(buildConfig(), true);
    expect(screen.getByRole("button", { name: "I'm Ready" })).toBeDisabled();
  });

  it("does not dispatch when the button is disabled and clicked", () => {
    const { onSendUserMessageToCoach } = renderCard(buildConfig(), true);
    fireEvent.click(screen.getByRole("button", { name: "I'm Ready" }));
    expect(onSendUserMessageToCoach).not.toHaveBeenCalled();
  });

  it("renders the coach message text alongside the button", () => {
    renderCard(buildConfig(), false, <span>Take a moment.</span>);
    expect(screen.getByText("Take a moment.")).toBeInTheDocument();
  });
});
