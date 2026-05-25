import { CoachingPhase } from "@/enums/coachingPhase";
import type { Identity } from "./identity";
import { GetToKnowYouQuestions } from "@/enums/getToKnowYouQuestions";

/**
 * Current state of the coaching session
 */
export interface CoachState {
  id: string;
  user: string; // User ID
  current_phase: CoachingPhase;
  current_identity?: Identity | null;
  proposed_identity?: Identity | null;
  identity_focus?: string | null;
  skipped_identity_categories?: string[] | null;
  who_you_are: string[] | null;
  who_you_want_to_be: string[] | null;
  asked_questions: GetToKnowYouQuestions[] | null;
  metadata?: {
    [k: string]: unknown;
  };
  updated_at: string;
  /**
   * Coaching Phase Videos (PR 9): true while the user has an open `Break`
   * row (between-session pause). Backend-derived from
   * `Break.objects.filter(user=u, ended_at__isnull=True).exists()`. The
   * chat composer disables when true so the user must click "I'm Ready"
   * before typing.
   */
  on_break?: boolean;
}
