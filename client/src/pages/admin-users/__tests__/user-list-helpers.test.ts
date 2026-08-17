import type { AdminUserListItem } from "@/api/adminUsers";
import { CoachingPhase } from "@/enums/coachingPhase";
import {
	filterUsers,
	nextPhaseSort,
	sortUsersByPhase,
} from "@/pages/admin-users/user-list-helpers";
import { describe, expect, it } from "vitest";

const makeUser = (
	overrides: Partial<AdminUserListItem> & { id: string },
): AdminUserListItem => ({
	email: `${overrides.id}@example.com`,
	first_name: "",
	last_name: "",
	is_active: true,
	is_staff: false,
	is_superuser: false,
	last_login: null,
	created_at: null,
	coaching_phase: null,
	is_test_user: false,
	test_scenario_name: null,
	...overrides,
});

const ids = (users: AdminUserListItem[]) => users.map((user) => user.id);

describe("filterUsers", () => {
	const real = makeUser({ id: "real", first_name: "Dana" });
	const test = makeUser({
		id: "test",
		is_test_user: true,
		test_scenario_name: "Brainstorm Dana",
	});

	it("hides test users unless the toggle is on", () => {
		expect(
			ids(filterUsers([real, test], { search: "", showTestUsers: false })),
		).toEqual(["real"]);
		expect(
			ids(filterUsers([real, test], { search: "", showTestUsers: true })),
		).toEqual(["real", "test"]);
	});

	it("keeps the test-user filter applied while searching", () => {
		// "Dana" matches the real user's name and the test scenario name.
		expect(
			ids(filterUsers([real, test], { search: "dana", showTestUsers: false })),
		).toEqual(["real"]);
		expect(
			ids(filterUsers([real, test], { search: "dana", showTestUsers: true })),
		).toEqual(["real", "test"]);
	});

	it("matches on email, name, phase, and scenario name", () => {
		const users = [
			makeUser({ id: "by-email", email: "someone@neovita.ai" }),
			makeUser({ id: "by-name", last_name: "Okafor" }),
			makeUser({
				id: "by-phase",
				coaching_phase: CoachingPhase.IDENTITY_WARMUP,
			}),
		];

		expect(
			ids(filterUsers(users, { search: "neovita", showTestUsers: true })),
		).toEqual(["by-email"]);
		expect(
			ids(filterUsers(users, { search: "okaf", showTestUsers: true })),
		).toEqual(["by-name"]);
		expect(
			ids(filterUsers(users, { search: "warm_up", showTestUsers: true })),
		).toEqual(["by-phase"]);
	});

	it("ignores surrounding whitespace in the search term", () => {
		expect(
			ids(filterUsers([real], { search: "  dana  ", showTestUsers: false })),
		).toEqual(["real"]);
	});
});

describe("sortUsersByPhase", () => {
	const early = makeUser({
		id: "early",
		coaching_phase: CoachingPhase.INTRODUCTION,
	});
	const middle = makeUser({
		id: "middle",
		coaching_phase: CoachingPhase.IDENTITY_REFINEMENT,
	});
	const late = makeUser({
		id: "late",
		coaching_phase: CoachingPhase.IDENTITY_VISUALIZATION,
	});
	const noPhase = makeUser({ id: "no-phase" });

	it("orders by coaching progression, not alphabetically", () => {
		// Alphabetically "Identity Refinement" precedes "Introduction"; by
		// progression it does not.
		expect(ids(sortUsersByPhase([middle, early, late], "asc"))).toEqual([
			"early",
			"middle",
			"late",
		]);
		expect(ids(sortUsersByPhase([middle, early, late], "desc"))).toEqual([
			"late",
			"middle",
			"early",
		]);
	});

	it("keeps users with no phase last in both directions", () => {
		expect(ids(sortUsersByPhase([noPhase, late, early], "asc"))).toEqual([
			"early",
			"late",
			"no-phase",
		]);
		expect(ids(sortUsersByPhase([noPhase, late, early], "desc"))).toEqual([
			"late",
			"early",
			"no-phase",
		]);
	});

	it("treats an unrecognized phase like no phase", () => {
		const unknown = makeUser({ id: "unknown", coaching_phase: "made_up" });
		expect(ids(sortUsersByPhase([unknown, early], "asc"))).toEqual([
			"early",
			"unknown",
		]);
	});

	it("leaves the list untouched when unsorted", () => {
		const input = [middle, early, late];
		expect(sortUsersByPhase(input, null)).toBe(input);
	});

	it("does not mutate the input array", () => {
		const input = [late, early];
		sortUsersByPhase(input, "asc");
		expect(ids(input)).toEqual(["late", "early"]);
	});
});

describe("nextPhaseSort", () => {
	it("cycles unsorted → ascending → descending → unsorted", () => {
		expect(nextPhaseSort(null)).toBe("asc");
		expect(nextPhaseSort("asc")).toBe("desc");
		expect(nextPhaseSort("desc")).toBeNull();
	});
});
