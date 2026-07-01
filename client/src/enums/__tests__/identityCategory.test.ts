import {
	IdentityCategory,
	getIdentityCategoryColor,
	getIdentityCategoryDarkColor,
	getIdentityCategoryDescription,
	getIdentityCategoryDisplayName,
	getIdentityCategoryIcon,
	getIdentityCategoryLightColor,
} from "@/enums/identityCategory";
import { FaUser } from "react-icons/fa";
import { describe, expect, it } from "vitest";

describe("getIdentityCategoryDisplayName", () => {
	it("returns display name for every category", () => {
		for (const category of Object.values(IdentityCategory)) {
			const name = getIdentityCategoryDisplayName(category);
			expect(name).toBeTruthy();
			expect(name).not.toBe(category);
		}
	});

	it("returns correct names for specific categories", () => {
		expect(getIdentityCategoryDisplayName("passions_and_talents")).toBe(
			"Passions and Talents",
		);
		expect(getIdentityCategoryDisplayName("maker_of_money")).toBe(
			"Maker of Money",
		);
	});

	it("handles case-insensitive matching", () => {
		expect(getIdentityCategoryDisplayName("PASSIONS_AND_TALENTS")).toBe(
			"Passions and Talents",
		);
	});

	it("returns original value for unrecognized category", () => {
		expect(getIdentityCategoryDisplayName("totally_new")).toBe("totally_new");
	});

	it("returns falsy input as-is", () => {
		expect(getIdentityCategoryDisplayName("")).toBe("");
	});
});

describe("getIdentityCategoryColor", () => {
	it("returns color classes for every category", () => {
		for (const category of Object.values(IdentityCategory)) {
			const color = getIdentityCategoryColor(category);
			expect(color).toContain("bg-");
			expect(color).toContain("text-");
		}
	});

	it("returns gray fallback for empty string", () => {
		expect(getIdentityCategoryColor("")).toContain("bg-gray");
	});

	it("returns gray fallback for unknown category", () => {
		expect(getIdentityCategoryColor("unknown")).toContain("bg-gray");
	});
});

describe("getIdentityCategoryLightColor", () => {
	it("returns light color for known category", () => {
		const color = getIdentityCategoryLightColor("passions_and_talents");
		expect(color).toContain("bg-orange-50");
	});

	it("returns gray fallback for unknown", () => {
		expect(getIdentityCategoryLightColor("unknown")).toContain("bg-gray-50");
	});
});

describe("getIdentityCategoryDarkColor", () => {
	it("returns dark color for known category", () => {
		const color = getIdentityCategoryDarkColor("passions_and_talents");
		expect(color).toContain("border-orange");
	});

	it("returns gray fallback for unknown", () => {
		expect(getIdentityCategoryDarkColor("unknown")).toContain("border-gray");
	});
});

describe("getIdentityCategoryIcon", () => {
	it("returns a component for every enum value", () => {
		for (const category of Object.values(IdentityCategory)) {
			const Icon = getIdentityCategoryIcon(category);
			expect(Icon).toBeDefined();
			expect(typeof Icon).toBe("function");
		}
	});

	it("returns FaUser as fallback for unknown category", () => {
		const Icon = getIdentityCategoryIcon("completely_unknown_category");
		expect(Icon).toBe(FaUser);
	});

	it("handles case-insensitive input", () => {
		const Icon = getIdentityCategoryIcon("PASSIONS_AND_TALENTS");
		expect(Icon).toBeDefined();
		expect(Icon).not.toBe(FaUser);
	});
});

describe("getIdentityCategoryDescription", () => {
	it("returns a description for every category", () => {
		for (const category of Object.values(IdentityCategory)) {
			const description = getIdentityCategoryDescription(category);
			expect(description).toBeTruthy();
		}
	});

	it("returns the expected description for a specific category", () => {
		expect(getIdentityCategoryDescription("maker_of_money")).toContain(
			"generate income",
		);
	});

	it("handles case-insensitive matching", () => {
		expect(getIdentityCategoryDescription("PASSIONS_AND_TALENTS")).toBe(
			getIdentityCategoryDescription("passions_and_talents"),
		);
	});

	it("returns empty string for unknown category", () => {
		expect(getIdentityCategoryDescription("totally_new")).toBe("");
	});

	it("returns empty string for empty input", () => {
		expect(getIdentityCategoryDescription("")).toBe("");
	});
});
