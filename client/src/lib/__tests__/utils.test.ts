import { cn } from "@/lib/utils";
import { describe, expect, it } from "vitest";

describe("cn", () => {
	it("merges class names", () => {
		expect(cn("foo", "bar")).toBe("foo bar");
	});

	it("handles conditional classes", () => {
		expect(cn("base", false && "hidden", "visible")).toBe("base visible");
	});

	it("deduplicates conflicting tailwind classes", () => {
		expect(cn("p-4", "p-2")).toBe("p-2");
		expect(cn("text-red-500", "text-blue-500")).toBe("text-blue-500");
	});

	it("handles empty/null/undefined inputs", () => {
		expect(cn("", undefined, null, "class")).toBe("class");
	});

	it("handles arrays of classes", () => {
		expect(cn(["foo", "bar"], "baz")).toBe("foo bar baz");
	});
});
