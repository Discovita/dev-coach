import { IdentityState } from "@/enums/identityState";
import { IdentityCategory } from "@/enums/identityCategory";

/**
 * Represents a single identity with its state.
 */
export interface Identity {
  id: string;
  description: string;
  state?: IdentityState;
  notes?: string[];
  category: IdentityCategory;
  created_at: string;
  updated_at: string;
}
