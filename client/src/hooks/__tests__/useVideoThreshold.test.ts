/**
 * Tests for useVideoThreshold (PR 17).
 *
 * Threshold rules per spec Decision 8:
 *   - Videos LONGER than 30s: enable Continue at (duration - 20)s
 *   - Videos ≤ 30s:           enable Continue at 50% of duration
 * Sticky once reached.
 */

import {
	END_THRESHOLD_SECONDS,
	SHORT_VIDEO_CUTOFF_SECONDS,
	useVideoThreshold,
} from "@/hooks/use-video-threshold";
import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";

describe("useVideoThreshold", () => {
	it("starts with thresholdReached=false", () => {
		const { result } = renderHook(() => useVideoThreshold());
		expect(result.current.thresholdReached).toBe(false);
	});

	it("returns disabled (false) before threshold for a long (>30s) video", () => {
		const { result } = renderHook(() => useVideoThreshold());
		act(() => {
			result.current.onTimeUpdate(10, 120); // threshold = 120 - 20 = 100s
		});
		expect(result.current.thresholdReached).toBe(false);
	});

	it("enables at the (duration - 20s) threshold for a long video", () => {
		const { result } = renderHook(() => useVideoThreshold());
		const duration = 120;
		const threshold = duration - END_THRESHOLD_SECONDS;

		act(() => {
			result.current.onTimeUpdate(threshold - 1, duration);
		});
		expect(result.current.thresholdReached).toBe(false);

		act(() => {
			result.current.onTimeUpdate(threshold, duration);
		});
		expect(result.current.thresholdReached).toBe(true);
	});

	it("enables at 50% for a short (≤30s) video", () => {
		const { result } = renderHook(() => useVideoThreshold());
		const duration = 20; // ≤ 30s — short video
		expect(duration).toBeLessThanOrEqual(SHORT_VIDEO_CUTOFF_SECONDS);

		act(() => {
			result.current.onTimeUpdate(duration * 0.49, duration);
		});
		expect(result.current.thresholdReached).toBe(false);

		act(() => {
			result.current.onTimeUpdate(duration * 0.5, duration);
		});
		expect(result.current.thresholdReached).toBe(true);
	});

	it("is sticky once reached — never flips back to false", () => {
		const { result } = renderHook(() => useVideoThreshold());
		act(() => {
			result.current.onTimeUpdate(110, 120); // > 100s → reached
		});
		expect(result.current.thresholdReached).toBe(true);

		act(() => {
			result.current.onTimeUpdate(5, 120); // user scrubs back
		});
		expect(result.current.thresholdReached).toBe(true);
	});

	it("ignores updates when duration is 0 or NaN (still-loading metadata)", () => {
		const { result } = renderHook(() => useVideoThreshold());
		act(() => {
			result.current.onTimeUpdate(0, 0);
			result.current.onTimeUpdate(5, Number.NaN);
		});
		expect(result.current.thresholdReached).toBe(false);
	});
});
