import type { ComponentConfig } from "./componentConfig";

/**
 * A single message in the conversation history.
 */
export interface Message {
	/**
	 * Stable identity for React keys. Server-persisted messages carry their
	 * DB UUID; optimistic/synthetic messages created client-side get a
	 * `client-*` id so a row keeps the same key from optimistic render through
	 * commit and never remounts (which would re-run its entrance animation and
	 * make the list flicker). Optional because historical payloads predate it.
	 */
	id?: string;
	role: string;
	content: string;
	timestamp: string;
	component_config?: ComponentConfig;
	/**
	 * True while this is a placeholder coach message awaiting the server
	 * response. The bubble shows the loading dots; when the response lands the
	 * SAME message is finalized in place (content filled, `pending` cleared) so
	 * the dots crossfade into the response inside one persistent bubble instead
	 * of a separate loading bubble unmounting (which made the dots "fall").
	 */
	pending?: boolean;
}
