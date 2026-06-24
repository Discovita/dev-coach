import {
	COACHING_PHASE_DISPLAY_NAMES,
	CoachingPhase,
	getCoachingPhaseColor,
	getCoachingPhaseDisplayName,
} from "@/enums/coachingPhase";
import { describe, expect, it } from "vitest";

describe("getCoachingPhaseDisplayName", () => {
	it("returns display name for every phase", () => {
		for (const phase of Object.values(CoachingPhase)) {
			const displayName = getCoachingPhaseDisplayName(phase);
			expect(displayName).toBeTruthy();
			expect(displayName).not.toBe(phase);
		}
	});

	it("returns the correct name for specific phases", () => {
		expect(getCoachingPhaseDisplayName(CoachingPhase.INTRODUCTION)).toBe(
			"Introduction",
		);
		expect(
			getCoachingPhaseDisplayName(CoachingPhase.IDENTITY_BRAINSTORMING),
		).toBe("Identity Brainstorming");
		expect(getCoachingPhaseDisplayName(CoachingPhase.I_AM_STATEMENT)).toBe(
			"I Am Statement",
		);
	});

	it("returns the raw value as fallback for unknown phase", () => {
		expect(getCoachingPhaseDisplayName("unknown_phase" as CoachingPhase)).toBe(
			"unknown_phase",
		);
	});

	it("covers all enum values in the display names map", () => {
		const phases = Object.values(CoachingPhase);
		const mappedPhases = Object.keys(COACHING_PHASE_DISPLAY_NAMES);
		expect(mappedPhases).toHaveLength(phases.length);
	});
});

describe("getCoachingPhaseColor", () => {
	it("returns color classes for every phase", () => {
		for (const phase of Object.values(CoachingPhase)) {
			const color = getCoachingPhaseColor(phase);
			expect(color).toContain("bg-");
			expect(color).toContain("text-");
		}
	});

	it("returns gray fallback for unknown phase", () => {
		const color = getCoachingPhaseColor("unknown" as CoachingPhase);
		expect(color).toContain("bg-gray");
	});
});
