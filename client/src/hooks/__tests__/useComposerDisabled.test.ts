/**
 * Tests for useComposerDisabled (PR 18).
 *
 * The composer disables when ANY of:
 *   - isProcessingMessage === true
 *   - coachState.on_break === true
 *   - latest coach message is a SESSION_VIDEO whose video_key is NOT
 *     in coachState.shown_videos
 *
 * The 2×2×2 truth-table assertion at the bottom locks the combination
 * semantics so a future refactor can't quietly turn ANY-of into ALL-of.
 */

import { CoachingPhase } from "@/enums/coachingPhase";
import { ComponentType } from "@/enums/componentType";
import { useComposerDisabled } from "@/hooks/use-composer-disabled";
import type { CoachState } from "@/types/coachState";
import type { Message } from "@/types/message";
import { renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/hooks/use-coach-state", () => ({
	useCoachState: vi.fn(),
}));

vi.mock("@/hooks/use-chat-messages", () => ({
	useChatMessages: vi.fn(),
}));

import { useChatMessages } from "@/hooks/use-chat-messages";
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
	on_break: false,
};

function mockCoachState(state: Partial<CoachState> | undefined = {}) {
	vi.mocked(useCoachState).mockReturnValue({
		coachState:
			state === undefined ? undefined : { ...baseCoachState, ...state },
		isLoading: false,
		isError: false,
		// biome-ignore lint/suspicious/noExplicitAny: test mock needs a loose return type
		refetchCoachState: vi.fn() as any,
	});
}

function mockChatMessages(messages: Message[] | undefined) {
	vi.mocked(useChatMessages).mockReturnValue({
		chatMessages: messages,
		componentConfig: null,
		isLoading: false,
		isError: false,
		refetchChatMessages: vi.fn(),
		updateChatMessages: vi.fn(),
		updateStatus: "idle",
		pendingMessage: undefined,
		isPending: false,
		isUpdateError: false,
		resetChatMessages: vi.fn(),
		resetStatus: "idle",
		// biome-ignore lint/suspicious/noExplicitAny: test mock needs a loose return type
	} as any);
}

function userMsg(content: string): Message {
	return { role: "user", content, timestamp: "2025-01-01" };
}

function coachMsg(
	content: string,
	componentConfig?: Message["component_config"],
): Message {
	return {
		role: "coach",
		content,
		timestamp: "2025-01-01",
		component_config: componentConfig,
	};
}

function sessionVideoMsg(videoKey: string): Message {
	return coachMsg("", {
		component_type: ComponentType.SESSION_VIDEO,
		video_key: videoKey,
		video_name: "Some Video",
		video_url: "https://example.com/v.mov",
	});
}

describe("useComposerDisabled", () => {
	beforeEach(() => {
		vi.mocked(useCoachState).mockReset();
		vi.mocked(useChatMessages).mockReset();
	});

	it("returns false when nothing is gating (baseline)", () => {
		mockCoachState({});
		mockChatMessages([userMsg("hi"), coachMsg("hello")]);
		const { result } = renderHook(() => useComposerDisabled(false));
		expect(result.current).toBe(false);
	});

	it("returns true when isProcessingMessage is true", () => {
		mockCoachState({});
		mockChatMessages([coachMsg("hello")]);
		const { result } = renderHook(() => useComposerDisabled(true));
		expect(result.current).toBe(true);
	});

	it("returns true when on_break is true regardless of latest message type", () => {
		mockCoachState({ on_break: true });
		mockChatMessages([coachMsg("hello")]);
		const { result } = renderHook(() => useComposerDisabled(false));
		expect(result.current).toBe(true);
	});

	it("returns true when latest coach message is SESSION_VIDEO and key NOT in shown_videos", () => {
		mockCoachState({ shown_videos: [] });
		mockChatMessages([sessionVideoMsg("welcome_session_intro")]);
		const { result } = renderHook(() => useComposerDisabled(false));
		expect(result.current).toBe(true);
	});

	it("returns false when latest SESSION_VIDEO key IS in shown_videos", () => {
		mockCoachState({ shown_videos: ["welcome_session_intro"] });
		mockChatMessages([sessionVideoMsg("welcome_session_intro")]);
		const { result } = renderHook(() => useComposerDisabled(false));
		expect(result.current).toBe(false);
	});

	it("returns false when an unacked SESSION_VIDEO is in history but NOT the latest coach message", () => {
		mockCoachState({ shown_videos: [] });
		mockChatMessages([
			sessionVideoMsg("welcome_session_intro"),
			coachMsg("Hi, I'm Leigh-Ann..."),
		]);
		const { result } = renderHook(() => useComposerDisabled(false));
		expect(result.current).toBe(false);
	});

	it("ignores trailing user messages when finding the latest COACH message", () => {
		// A user message after the unacked SESSION_VIDEO should not change the
		// gating — the latest *coach* message is still the video.
		mockCoachState({ shown_videos: [] });
		mockChatMessages([
			sessionVideoMsg("welcome_session_intro"),
			userMsg("trying to type past it"),
		]);
		const { result } = renderHook(() => useComposerDisabled(false));
		expect(result.current).toBe(true);
	});

	it("returns false when chatMessages is undefined (initial load)", () => {
		mockCoachState({});
		mockChatMessages(undefined);
		const { result } = renderHook(() => useComposerDisabled(false));
		expect(result.current).toBe(false);
	});

	it("returns false when coachState is undefined (initial load)", () => {
		mockCoachState(undefined);
		mockChatMessages([sessionVideoMsg("welcome_session_intro")]);
		// No coachState → no on_break gate; shown_videos defaults to empty;
		// but latest is SESSION_VIDEO with no shown_videos → still gated.
		const { result } = renderHook(() => useComposerDisabled(false));
		expect(result.current).toBe(true);
	});

	it("treats missing shown_videos as 'never acked' (graceful)", () => {
		mockCoachState({ shown_videos: undefined });
		mockChatMessages([sessionVideoMsg("welcome_session_intro")]);
		const { result } = renderHook(() => useComposerDisabled(false));
		expect(result.current).toBe(true);
	});

	it("does not gate when latest coach message has no component_config", () => {
		mockCoachState({});
		mockChatMessages([coachMsg("just text, no component")]);
		const { result } = renderHook(() => useComposerDisabled(false));
		expect(result.current).toBe(false);
	});

	it("does not gate when latest coach message is a non-SESSION_VIDEO component", () => {
		mockCoachState({});
		mockChatMessages([
			coachMsg("Pick one", {
				component_type: ComponentType.COMBINE_IDENTITIES,
			}),
		]);
		const { result } = renderHook(() => useComposerDisabled(false));
		expect(result.current).toBe(false);
	});

	// Truth-table coverage over (on_break × latest_is_unacked_video × processing).
	// Disabled iff ANY input is true; enabled only when all three are false.
	describe("truth table: on_break × latest_is_unacked_video × processing", () => {
		const cases: Array<{
			onBreak: boolean;
			unackedVideo: boolean;
			processing: boolean;
			expected: boolean;
		}> = [
			{
				onBreak: false,
				unackedVideo: false,
				processing: false,
				expected: false,
			},
			{ onBreak: false, unackedVideo: false, processing: true, expected: true },
			{ onBreak: false, unackedVideo: true, processing: false, expected: true },
			{ onBreak: false, unackedVideo: true, processing: true, expected: true },
			{ onBreak: true, unackedVideo: false, processing: false, expected: true },
			{ onBreak: true, unackedVideo: false, processing: true, expected: true },
			{ onBreak: true, unackedVideo: true, processing: false, expected: true },
			{ onBreak: true, unackedVideo: true, processing: true, expected: true },
		];

		it.each(cases)(
			"on_break=$onBreak, unackedVideo=$unackedVideo, processing=$processing → disabled=$expected",
			({ onBreak, unackedVideo, processing, expected }) => {
				mockCoachState({
					on_break: onBreak,
					shown_videos: unackedVideo ? [] : ["welcome_session_intro"],
				});
				mockChatMessages([sessionVideoMsg("welcome_session_intro")]);
				const { result } = renderHook(() => useComposerDisabled(processing));
				expect(result.current).toBe(expected);
			},
		);
	});
});
