import { useIsMobile } from "@/hooks/use-mobile";
import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

describe("useIsMobile", () => {
	let listeners: Array<() => void>;

	beforeEach(() => {
		listeners = [];
		vi.stubGlobal(
			"matchMedia",
			vi.fn().mockImplementation((query: string) => ({
				matches: false,
				media: query,
				addEventListener: (_: string, cb: () => void) => {
					listeners.push(cb);
				},
				removeEventListener: (_: string, cb: () => void) => {
					listeners = listeners.filter((l) => l !== cb);
				},
			})),
		);
	});

	it("returns false when window is wider than breakpoint", () => {
		vi.stubGlobal("innerWidth", 1024);
		const { result } = renderHook(() => useIsMobile());
		expect(result.current).toBe(false);
	});

	it("returns true when window is narrower than breakpoint", () => {
		vi.stubGlobal("innerWidth", 600);
		const { result } = renderHook(() => useIsMobile());
		expect(result.current).toBe(true);
	});

	it("updates when window resizes across breakpoint", () => {
		vi.stubGlobal("innerWidth", 1024);
		const { result } = renderHook(() => useIsMobile());
		expect(result.current).toBe(false);

		vi.stubGlobal("innerWidth", 600);
		act(() => {
			for (const listener of listeners) listener();
		});
		expect(result.current).toBe(true);
	});

	it("cleans up event listener on unmount", () => {
		vi.stubGlobal("innerWidth", 1024);
		const { unmount } = renderHook(() => useIsMobile());
		const listenerCountBefore = listeners.length;
		unmount();
		expect(listeners.length).toBeLessThan(listenerCountBefore);
	});
});
