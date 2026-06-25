import { CoachingPhase } from "@/enums/coachingPhase";
import {
	STUDIO_LOCKED_MESSAGE,
	VISUALIZATION_INTRO_VIDEO_KEY,
	isCoachingComplete,
	isStudioLocked,
} from "@/lib/studio-lock";
import type { CoachState } from "@/types/coachState";
import { describe, expect, it } from "vitest";

function coachStateInPhase(
	phase: CoachingPhase,
	shownVideos: string[] = [],
): CoachState {
	return {
		id: "cs-1",
		user: "user-1",
		current_phase: phase,
		who_you_are: null,
		who_you_want_to_be: null,
		asked_questions: null,
		shown_videos: shownVideos,
		updated_at: "2026-01-01T00:00:00Z",
	};
}

describe("isStudioLocked", () => {
	it("is unlocked only in the identity visualization phase", () => {
		expect(
			isStudioLocked(coachStateInPhase(CoachingPhase.IDENTITY_VISUALIZATION)),
		).toBe(false);
	});

	it("is locked in every other phase", () => {
		const otherPhases = Object.values(CoachingPhase).filter(
			(p) => p !== CoachingPhase.IDENTITY_VISUALIZATION,
		);
		for (const phase of otherPhases) {
			expect(isStudioLocked(coachStateInPhase(phase))).toBe(true);
		}
	});

	it("is locked when the coach state is unknown (still loading / failed)", () => {
		expect(isStudioLocked(undefined)).toBe(true);
	});

	it("exposes a stable user-facing message", () => {
		expect(STUDIO_LOCKED_MESSAGE).toBe("This isn't available yet.");
	});

	describe("studio_access_override", () => {
		it("force-unlocks an early phase when override is true", () => {
			const state = coachStateInPhase(CoachingPhase.INTRODUCTION);
			state.studio_access_override = true;
			expect(isStudioLocked(state)).toBe(false);
		});

		it("force-locks the visualization phase when override is false", () => {
			const state = coachStateInPhase(CoachingPhase.IDENTITY_VISUALIZATION);
			state.studio_access_override = false;
			expect(isStudioLocked(state)).toBe(true);
		});

		it("falls back to phase-based behavior when override is null", () => {
			const visualization = coachStateInPhase(
				CoachingPhase.IDENTITY_VISUALIZATION,
			);
			visualization.studio_access_override = null;
			expect(isStudioLocked(visualization)).toBe(false);

			const early = coachStateInPhase(CoachingPhase.INTRODUCTION);
			early.studio_access_override = null;
			expect(isStudioLocked(early)).toBe(true);
		});
	});
});

describe("isCoachingComplete", () => {
	it("is false in the visualization phase until the intro video is acked", () => {
		// Phase flips to visualization early (before the intro video), so the
		// phase alone must NOT mark coaching complete.
		expect(
			isCoachingComplete(
				coachStateInPhase(CoachingPhase.IDENTITY_VISUALIZATION, []),
			),
		).toBe(false);
	});

	it("is true once the visualization intro video is acknowledged", () => {
		expect(
			isCoachingComplete(
				coachStateInPhase(CoachingPhase.IDENTITY_VISUALIZATION, [
					VISUALIZATION_INTRO_VIDEO_KEY,
				]),
			),
		).toBe(true);
	});

	it("is false outside the visualization phase even if the key is present", () => {
		expect(
			isCoachingComplete(
				coachStateInPhase(CoachingPhase.I_AM_STATEMENT, [
					VISUALIZATION_INTRO_VIDEO_KEY,
				]),
			),
		).toBe(false);
	});

	it("is false for an unknown coach state", () => {
		expect(isCoachingComplete(undefined)).toBe(false);
	});
});
