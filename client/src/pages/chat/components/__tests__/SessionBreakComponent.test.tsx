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

import { ActionType } from "@/enums/actionType";
import { ComponentType } from "@/enums/componentType";
import { SessionBreakComponent } from "@/pages/chat/components/coach-message-with-component/SessionBreakComponent";
import type { ComponentConfig } from "@/types/componentConfig";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

function buildConfig(
	overrides: Partial<ComponentConfig> = {},
): ComponentConfig {
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
	onSendUserMessageToCoach = vi.fn(),
) {
	const result = render(
		<SessionBreakComponent
			coachMessage={coachMessage}
			config={config}
			onSendUserMessageToCoach={onSendUserMessageToCoach}
			disabled={disabled}
		/>,
	);
	return { ...result, onSendUserMessageToCoach };
}

describe("SessionBreakComponent (PR 18)", () => {
	it("renders the I'm Ready button using config.buttons[0].label", () => {
		renderCard();
		expect(
			screen.getByRole("button", { name: "I'm Ready" }),
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
						{
							action: "log_break_resumed" as ActionType,
							params: { source: "ui" },
						},
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

	it("renders coach message text above the card when content is non-empty", () => {
		// Mirrors ChatMessages.tsx: passes a MarkdownRenderer-shaped element
		// with a `content` prop. The component peeks at that prop to decide
		// whether to render a coach bubble above the break card. Mirrors
		// SessionVideoCard's `extractContentString` behavior.
		const Fake = ({ content }: { content: string }) => (
			<div data-testid="coach-text">{content}</div>
		);
		renderCard(buildConfig(), false, <Fake content="Take a moment." />);
		expect(screen.getByText("Take a moment.")).toBeInTheDocument();
	});

	it("suppresses the coach text bubble when content is empty (skip-LLM path)", () => {
		// The skip-LLM path writes the break card with `content=""` (the
		// component IS the turn). No coach bubble should render above the
		// card in that case.
		const Fake = ({ content }: { content: string }) => (
			<div data-testid="coach-text">{content || "should-not-render"}</div>
		);
		renderCard(buildConfig(), false, <Fake content="" />);
		expect(screen.queryByTestId("coach-text")).not.toBeInTheDocument();
	});

	// ----- Visual chrome (the "make it obvious you're on a break" pass) ---

	it("renders the 'Time for a Break' heading", () => {
		renderCard();
		expect(screen.getByText("Time for a Break")).toBeInTheDocument();
	});

	it("renders the descriptive break copy", () => {
		renderCard();
		expect(screen.getByText(/ready and rested/i)).toBeInTheDocument();
	});

	it("renders inside the break-card container", () => {
		renderCard();
		expect(screen.getByTestId("session-break-card")).toBeInTheDocument();
	});

	// ----- Closed (historical) state -------------------------------------

	it("renders the compact closed marker when config.closed=true", () => {
		renderCard(
			buildConfig({
				closed: true,
				started_at: "2026-05-26T12:00:00Z",
				ended_at: "2026-05-26T12:23:00Z",
				buttons: undefined, // end_break strips buttons on close
			}),
		);
		expect(screen.getByTestId("session-break-card-closed")).toBeInTheDocument();
		expect(screen.queryByTestId("session-break-card")).not.toBeInTheDocument();
	});

	it("does not render the I'm Ready button when closed", () => {
		renderCard(
			buildConfig({
				closed: true,
				started_at: "2026-05-26T12:00:00Z",
				ended_at: "2026-05-26T12:10:00Z",
				buttons: undefined,
			}),
		);
		expect(
			screen.queryByRole("button", { name: "I'm Ready" }),
		).not.toBeInTheDocument();
	});

	it("does not render the heading or descriptive copy when closed", () => {
		renderCard(
			buildConfig({
				closed: true,
				started_at: "2026-05-26T12:00:00Z",
				ended_at: "2026-05-26T12:10:00Z",
				buttons: undefined,
			}),
		);
		expect(screen.queryByText("Time for a Break")).not.toBeInTheDocument();
		expect(screen.queryByText(/ready and rested/i)).not.toBeInTheDocument();
	});

	it("formats duration in minutes for a multi-minute break", () => {
		renderCard(
			buildConfig({
				closed: true,
				started_at: "2026-05-26T12:00:00Z",
				ended_at: "2026-05-26T12:23:00Z",
				buttons: undefined,
			}),
		);
		expect(screen.getByText(/23 minutes/)).toBeInTheDocument();
	});

	it("formats duration as 'less than a minute' for a sub-minute break", () => {
		renderCard(
			buildConfig({
				closed: true,
				started_at: "2026-05-26T12:00:00Z",
				ended_at: "2026-05-26T12:00:30Z",
				buttons: undefined,
			}),
		);
		expect(screen.getByText(/less than a minute/)).toBeInTheDocument();
	});

	it("formats duration with hours and minutes for a long break", () => {
		renderCard(
			buildConfig({
				closed: true,
				started_at: "2026-05-26T12:00:00Z",
				ended_at: "2026-05-26T14:30:00Z",
				buttons: undefined,
			}),
		);
		expect(screen.getByText(/2h 30m/)).toBeInTheDocument();
	});

	it("renders 'Took a break' even when timestamps are missing (graceful)", () => {
		// Defensive: an older closed break written before timestamps were
		// captured (or a malformed row) should still render the marker
		// without crashing.
		renderCard(
			buildConfig({
				closed: true,
				buttons: undefined,
			}),
		);
		expect(screen.getByText(/Took a break/)).toBeInTheDocument();
	});

	it("does not dispatch on click in closed state (no button to click)", () => {
		const onSendUserMessageToCoach = vi.fn();
		renderCard(
			buildConfig({
				closed: true,
				started_at: "2026-05-26T12:00:00Z",
				ended_at: "2026-05-26T12:10:00Z",
				buttons: undefined,
			}),
			false,
			null,
			onSendUserMessageToCoach,
		);
		expect(onSendUserMessageToCoach).not.toHaveBeenCalled();
	});
});
