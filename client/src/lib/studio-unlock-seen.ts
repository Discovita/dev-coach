/**
 * Tracks whether the one-time Studio unlock animation has already played for
 * a given user, so it takes over the screen exactly once (right after the
 * visualization intro video) and not on every subsequent visit to the chat
 * while coaching is complete.
 *
 * Persisted in localStorage, keyed by user id. This is a celebratory, purely
 * presentational moment, so client-only persistence is sufficient — there is
 * no backend flag. (Consequence: it can replay on a brand-new device/browser,
 * and clearing the key re-arms it for testing.)
 */

const KEY_PREFIX = "studio-unlock-seen:";

function key(userId: string): string {
	return `${KEY_PREFIX}${userId}`;
}

export function hasSeenStudioUnlock(userId: string | null): boolean {
	if (!userId) return true; // no identity → don't show the takeover
	try {
		return localStorage.getItem(key(userId)) === "1";
	} catch {
		// localStorage unavailable (privacy mode, SSR) → treat as seen so we
		// never get stuck replaying it.
		return true;
	}
}

export function markStudioUnlockSeen(userId: string | null): void {
	if (!userId) return;
	try {
		localStorage.setItem(key(userId), "1");
	} catch {
		// Best-effort; if we can't persist, the worst case is it replays.
	}
}
