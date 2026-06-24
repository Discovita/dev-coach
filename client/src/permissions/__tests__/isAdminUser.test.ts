import { isAdminUser } from "@/permissions/isAdminUser";
import type { User } from "@/types/user";
import { describe, expect, it } from "vitest";

const baseUser: User = {
	id: "user-1",
	email: "test@test.com",
	created_at: "2025-01-01",
	updated_at: "2025-01-01",
};

describe("isAdminUser", () => {
	it("returns false for null", () => {
		expect(isAdminUser(null)).toBe(false);
	});

	it("returns false for undefined", () => {
		expect(isAdminUser(undefined)).toBe(false);
	});

	it("returns false for regular user", () => {
		expect(
			isAdminUser({ ...baseUser, is_staff: false, is_superuser: false }),
		).toBe(false);
	});

	it("returns true for staff user", () => {
		expect(
			isAdminUser({ ...baseUser, is_staff: true, is_superuser: false }),
		).toBe(true);
	});

	it("returns true for superuser", () => {
		expect(
			isAdminUser({ ...baseUser, is_staff: false, is_superuser: true }),
		).toBe(true);
	});

	it("returns true for user who is both staff and superuser", () => {
		expect(
			isAdminUser({ ...baseUser, is_staff: true, is_superuser: true }),
		).toBe(true);
	});

	it("returns false when is_staff and is_superuser are undefined", () => {
		expect(isAdminUser(baseUser)).toBe(false);
	});
});
