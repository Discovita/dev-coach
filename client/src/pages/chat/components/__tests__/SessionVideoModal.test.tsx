/**
 * Tests for SessionVideoModal — PR 17 Continue button + dispatch.
 *
 * Covers:
 *   - Continue button rendered for active (unacked) modal; hidden in
 *     Watch Again (acked) modal.
 *   - Continue disabled at video start; enabled once threshold reached.
 *   - Continue click for intro / outro dispatches the right actions.
 *   - Continue click closes the modal.
 *   - Esc / backdrop / X close still fire no dispatch.
 */

import { ActionType } from "@/enums/actionType";
import { SessionVideoModal } from "@/pages/chat/components/coach-message-with-component/SessionVideoModal";
import type { ComponentAction } from "@/types/componentConfig";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const intro_actions: ComponentAction[] = [
	{
		action: ActionType.ACKNOWLEDGE_SESSION_VIDEO,
		params: { video_key: "brainstorming_session_intro" },
	},
];

const outro_actions: ComponentAction[] = [
	{
		action: ActionType.ACKNOWLEDGE_SESSION_VIDEO,
		params: { video_key: "get_to_know_session_outro" },
	},
	{
		action: ActionType.START_BREAK,
		params: { session_key: "get_to_know_session" },
	},
];

const baseProps = {
	open: true,
	videoName: "Brainstorming Intro",
	videoUrl:
		"https://discovita-dev-coach-staging.s3.amazonaws.com/media/session-videos/04-brainstorming-session-intro.mov",
};

function fireTimeUpdate(currentTime: number, duration: number) {
	const video = screen.getByTestId("session-video-element") as HTMLVideoElement;
	// jsdom doesn't compute these — set them ourselves before firing the event.
	Object.defineProperty(video, "currentTime", {
		configurable: true,
		value: currentTime,
	});
	Object.defineProperty(video, "duration", {
		configurable: true,
		value: duration,
	});
	fireEvent.timeUpdate(video);
}

describe("SessionVideoModal — Continue button + dispatch (PR 17)", () => {
	let onContinue: ReturnType<typeof vi.fn>;
	let onOpenChange: ReturnType<typeof vi.fn>;

	beforeEach(() => {
		onContinue = vi.fn();
		onOpenChange = vi.fn();
	});

	// --- Visibility -----------------------------------------------------

	it("renders a Continue button for the active (unacked) modal", () => {
		render(
			<SessionVideoModal
				{...baseProps}
				onOpenChange={onOpenChange}
				acknowledged={false}
				actions={intro_actions}
				onContinue={onContinue}
			/>,
		);
		expect(screen.getByTestId("session-video-continue")).toBeInTheDocument();
	});

	it("does NOT render Continue for the Watch Again (acked) modal", () => {
		render(
			<SessionVideoModal
				{...baseProps}
				onOpenChange={onOpenChange}
				acknowledged={true}
				actions={intro_actions}
				onContinue={onContinue}
			/>,
		);
		expect(
			screen.queryByTestId("session-video-continue"),
		).not.toBeInTheDocument();
	});

	// --- Threshold gate -------------------------------------------------

	it("Continue is disabled at the start of the video", () => {
		render(
			<SessionVideoModal
				{...baseProps}
				onOpenChange={onOpenChange}
				acknowledged={false}
				actions={intro_actions}
				onContinue={onContinue}
			/>,
		);
		expect(screen.getByTestId("session-video-continue")).toBeDisabled();
	});

	it("Continue enables at (duration - 20s) for a long video (> 30s)", () => {
		render(
			<SessionVideoModal
				{...baseProps}
				onOpenChange={onOpenChange}
				acknowledged={false}
				actions={intro_actions}
				onContinue={onContinue}
			/>,
		);
		const btn = screen.getByTestId("session-video-continue");
		fireTimeUpdate(99, 120); // 120 - 20 = 100; 99 is still below
		expect(btn).toBeDisabled();
		fireTimeUpdate(100, 120);
		expect(btn).not.toBeDisabled();
	});

	it("Continue enables at 50% for a short video (≤ 30s)", () => {
		render(
			<SessionVideoModal
				{...baseProps}
				onOpenChange={onOpenChange}
				acknowledged={false}
				actions={intro_actions}
				onContinue={onContinue}
			/>,
		);
		const btn = screen.getByTestId("session-video-continue");
		fireTimeUpdate(9, 20); // < 10s = 50%
		expect(btn).toBeDisabled();
		fireTimeUpdate(10, 20);
		expect(btn).not.toBeDisabled();
	});

	// --- Dispatch shapes ------------------------------------------------

	it("Continue click for an intro video dispatches [ACK(video_key)]", () => {
		render(
			<SessionVideoModal
				{...baseProps}
				onOpenChange={onOpenChange}
				acknowledged={false}
				actions={intro_actions}
				onContinue={onContinue}
			/>,
		);
		fireTimeUpdate(110, 120);
		fireEvent.click(screen.getByTestId("session-video-continue"));

		expect(onContinue).toHaveBeenCalledTimes(1);
		expect(onContinue).toHaveBeenCalledWith(intro_actions);
	});

	it("Continue click for an outro video dispatches [ACK, START_BREAK]", () => {
		render(
			<SessionVideoModal
				{...baseProps}
				videoName="Get to Know You Outro"
				onOpenChange={onOpenChange}
				acknowledged={false}
				actions={outro_actions}
				onContinue={onContinue}
			/>,
		);
		fireTimeUpdate(110, 120);
		fireEvent.click(screen.getByTestId("session-video-continue"));

		expect(onContinue).toHaveBeenCalledTimes(1);
		const dispatched = onContinue.mock.calls[0][0] as ComponentAction[];
		expect(dispatched).toEqual(outro_actions);
		expect(dispatched).toHaveLength(2);
		expect(dispatched[1].action).toBe(ActionType.START_BREAK);
		expect(dispatched[1].params).toEqual({
			session_key: "get_to_know_session",
		});
	});

	it("Continue click closes the modal (onOpenChange(false))", () => {
		render(
			<SessionVideoModal
				{...baseProps}
				onOpenChange={onOpenChange}
				acknowledged={false}
				actions={intro_actions}
				onContinue={onContinue}
			/>,
		);
		fireTimeUpdate(110, 120);
		fireEvent.click(screen.getByTestId("session-video-continue"));

		expect(onOpenChange).toHaveBeenCalledWith(false);
	});

	// --- Non-dispatching close paths ------------------------------------

	it("Escape close fires onOpenChange(false) but does NOT dispatch", () => {
		render(
			<SessionVideoModal
				{...baseProps}
				onOpenChange={onOpenChange}
				acknowledged={false}
				actions={intro_actions}
				onContinue={onContinue}
			/>,
		);
		fireEvent.keyDown(document.body, { key: "Escape" });
		expect(onOpenChange).toHaveBeenCalledWith(false);
		expect(onContinue).not.toHaveBeenCalled();
	});

	it("X close button does NOT dispatch", () => {
		render(
			<SessionVideoModal
				{...baseProps}
				onOpenChange={onOpenChange}
				acknowledged={false}
				actions={intro_actions}
				onContinue={onContinue}
			/>,
		);
		const closeButton = screen.getByRole("button", { name: /close/i });
		fireEvent.click(closeButton);

		expect(onContinue).not.toHaveBeenCalled();
	});

	// --- Watch Again (acked) modal — no dispatch path at all -----------

	it("Watch Again modal has no Continue and no dispatch", () => {
		render(
			<SessionVideoModal
				{...baseProps}
				onOpenChange={onOpenChange}
				acknowledged={true}
				actions={intro_actions}
				onContinue={onContinue}
			/>,
		);
		fireTimeUpdate(110, 120);
		expect(
			screen.queryByTestId("session-video-continue"),
		).not.toBeInTheDocument();
		expect(onContinue).not.toHaveBeenCalled();
	});
});
