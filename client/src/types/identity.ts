import { IdentityCategory } from "@/enums/identityCategory";
import { IdentityState } from "@/enums/identityState";

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
  /** Notes about the identity (optional) */
  notes?: string[];
  /** Category this identity belongs to */
  category: IdentityCategory;
  /** Current state of the identity (optional) */
  state?: IdentityState;
  /** Created timestamp (optional) */
  created_at?: string;
  /** Updated timestamp (optional) */
  updated_at?: string;
}
