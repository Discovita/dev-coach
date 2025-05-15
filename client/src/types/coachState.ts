import { CoachingPhase } from "@/enums/coachingPhase";
import { Identity } from "./identity";

/**
 * Current state of the coaching session
 */
export interface CoachState {
  id: string;
  user: string; // User ID
  current_state: CoachingPhase;
  current_identity?: Identity | null;
  proposed_identity?: Identity | null;
  goals?: string[];
  metadata?: {
    [k: string]: unknown;
  };
  updated_at: string;
}
