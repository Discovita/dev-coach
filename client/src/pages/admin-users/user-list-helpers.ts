import type { AdminUserListItem } from "@/api/adminUsers";
import { CoachingPhase } from "@/enums/coachingPhase";

/**
 * Filtering and sorting helpers for the admin user list.
 *
 * Kept out of the component so the ordering rules — which follow the
 * coaching progression, not the alphabet — are directly testable.
 */

/**
 * The coaching phases in progression order. CoachingPhase is declared in the
 * order a user moves through it, so its position is the sort key.
 */
const PHASE_ORDER = Object.values(CoachingPhase);

/** Sort direction for the Phase column. `null` means "leave the list alone". */
export type PhaseSort = "asc" | "desc" | null;

/**
 * Position of a phase in the coaching progression. Users with no phase, or
 * with a phase the client doesn't know about, sort after everyone else in
 * both directions — they are not "before the introduction", they are unknown.
 */
const phaseRank = (phase: string | null): number => {
	if (!phase) return Number.POSITIVE_INFINITY;
	const index = PHASE_ORDER.indexOf(phase as CoachingPhase);
	return index === -1 ? Number.POSITIVE_INFINITY : index;
};

export interface UserFilters {
	search: string;
	showTestUsers: boolean;
}

/**
 * Apply the search box and the test-user toggle. Search matches name, email,
 * coaching phase, or test scenario name.
 */
export const filterUsers = (
	users: AdminUserListItem[],
	{ search, showTestUsers }: UserFilters,
): AdminUserListItem[] => {
	const term = search.trim().toLowerCase();

	return users.filter((user) => {
		if (!showTestUsers && user.is_test_user) return false;
		if (!term) return true;
		return (
			user.email.toLowerCase().includes(term) ||
			(user.first_name ?? "").toLowerCase().includes(term) ||
			(user.last_name ?? "").toLowerCase().includes(term) ||
			(user.coaching_phase ?? "").toLowerCase().includes(term) ||
			(user.test_scenario_name ?? "").toLowerCase().includes(term)
		);
	});
};

/**
 * Order by coaching progression. Returns a new array; the input order is
 * preserved when sort is null, and is the tiebreaker within a phase.
 */
export const sortUsersByPhase = (
	users: AdminUserListItem[],
	sort: PhaseSort,
): AdminUserListItem[] => {
	if (!sort) return users;

	return [...users].sort((a, b) => {
		const rankA = phaseRank(a.coaching_phase);
		const rankB = phaseRank(b.coaching_phase);
		if (rankA === rankB) return 0;
		// Unknown phases stay at the bottom regardless of direction.
		if (rankA === Number.POSITIVE_INFINITY) return 1;
		if (rankB === Number.POSITIVE_INFINITY) return -1;
		return sort === "asc" ? rankA - rankB : rankB - rankA;
	});
};

/** Click cycle for the Phase header: unsorted → ascending → descending. */
export const nextPhaseSort = (sort: PhaseSort): PhaseSort => {
	if (sort === null) return "asc";
	if (sort === "asc") return "desc";
	return null;
};
