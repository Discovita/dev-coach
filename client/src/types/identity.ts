import { IdentityCategory } from "@/enums/identityCategory";

/**
 * Represents a single identity with its state for test scenario editing.
 * Matches backend Identity model fields.
 */
export interface IdentityFormValue {
  /** Unique identifier (optional for new identities) */
  id?: string;
  /** Name/label for the identity (required) */
  name: string;
  /** Affirmation statement (optional) */
  affirmation?: string;
  /** Visualization (optional) */
  visualization?: string;
  /** Notes about the identity (optional) */
  notes?: string[];
  /** Category this identity belongs to */
  category: IdentityCategory;
  /** Created timestamp (optional) */
  created_at?: string;
  /** Updated timestamp (optional) */
  updated_at?: string;
}
