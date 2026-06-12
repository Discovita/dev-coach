import type { IdentityCategory } from "@/enums/identityCategory";
import type { IdentityState } from "@/enums/identityState";
import type { ImageSizes } from "@/types/imageSizes";

/**
 * Represents a single identity with its state for test scenario editing.
 * Matches backend Identity model fields.
 */
export interface Identity {
	/** Unique identifier (optional for new identities) */
	id?: string;
	/** Name/label for the identity (required) */
	name: string;
	/** I Am statement (optional) */
	i_am_statement?: string;
	/** Visualization (optional) */
	visualization?: string;
	/** Image URLs for different sizes (optional) */
	image?: ImageSizes | null;
	/** Notes about the identity (optional) */
	notes?: string[];
	/** Category this identity belongs to */
	category: IdentityCategory;
	/** Current state of the identity (optional) */
	state?: IdentityState;
	/** Scene: What clothing/attire for visualization (optional) */
	clothing?: string | null;
	/** Scene: What mood/feeling for visualization (optional) */
	mood?: string | null;
	/** Scene: What setting/environment for visualization (optional) */
	setting?: string | null;
	/** User-controlled display order, ascending (set via the reorder endpoint) */
	order?: number;
	/** Created timestamp (optional) */
	created_at?: string;
	/** Updated timestamp (optional) */
	updated_at?: string;
}

/**
 * Request payload for partially updating an identity. All fields are
 * optional — only the provided keys are changed (PATCH semantics).
 */
export interface UpdateIdentityRequest {
	/** Identity name/title */
	name?: string;
	/** I Am statement (null clears it) */
	i_am_statement?: string | null;
	/** Category bucket */
	category?: IdentityCategory;
	/** Scene: clothing/attire for visualization */
	clothing?: string | null;
	/** Scene: mood/feeling for visualization */
	mood?: string | null;
	/** Scene: setting/environment for visualization */
	setting?: string | null;
}
