import { CoachingPhase } from "@/enums/coachingPhase";
import { IdentityCategory } from "@/enums/identityCategory";
import { IdentityState } from "@/enums/identityState";
import { GetToKnowYouQuestions } from "@/enums/getToKnowYouQuestions";
import { ActionType } from "@/enums/actionType";

export interface TestScenarioUser {
  /**
   * The unique id for the test user (used for API calls to fetch user data).
   * Set by the backend in the test scenario serializer.
   */
  id?: string | number;
  first_name: string;
  last_name: string;
  /**
   * The email for the test user, if available (set by backend).
   * Only for display; do not send to backend on update/create.
   */
  email?: string;
  /**
   * The password for the test user, if available (set by backend, always 'Coach123!').
   * Only for display; do not send to backend on update/create.
   */
  password?: string;
}

export interface TestScenarioCoachState {
  current_phase?: CoachingPhase;
  identity_focus?: IdentityCategory;
  skipped_identity_categories?: IdentityCategory[];
  who_you_are?: string[];
  who_you_want_to_be?: string[];
  asked_questions?: GetToKnowYouQuestions[];
  current_identity?: string;
  /**
   * Coaching Phase Videos: session-video keys the user has acknowledged
   * (e.g. `"welcome_session_intro"`). Determines which intro/outro cards
   * the scenario replays as still-pending vs already-watched.
   */
  shown_videos?: string[];
}

export interface TestScenarioBreak {
  /**
   * Session key the user was leaving when the break opened
   * (e.g. `"brainstorming_session"`). Required.
   */
  triggered_by_session: string;
  /**
   * Optional. When the break opened. Preserved at instantiation via
   * `.update()` to bypass the model's `auto_now_add`.
   */
  started_at?: string;
  /**
   * Optional. When the user clicked "I'm Ready". Null/missing while the
   * break is still open — drives the `on_break` flag.
   */
  ended_at?: string;
  /**
   * Optional. ID of the original coach message carrying the
   * SESSION_BREAK component, for resolver-based re-linking during
   * instantiation.
   */
  original_coach_message_id?: string;
}

export interface TestScenarioIdentity {
  name: string;
  category: IdentityCategory;
  state?: IdentityState;
  i_am_statement?: string;
  visualization?: string;
  notes?: string[];
  /**
   * S3 URL for the image (stored as string in test scenario template).
   * Note: When identities are fetched directly from the API (not from template),
   * use the Identity type which has image as ImageSizes object with multiple sizes.
   */
  image?: string;
}

export interface TestScenarioChatMessage {
  role: string;
  content: string;
}

export interface TestScenarioUserNote {
  note: string;
}

export interface TestScenarioAction {
  action_type: ActionType;
  parameters: Record<string, unknown>;
  result_summary?: string;
  timestamp?: string;
  coach_message_content?: string;
}

export interface TestScenarioTemplate {
  user: TestScenarioUser;
  coach_state?: TestScenarioCoachState;
  identities?: TestScenarioIdentity[];
  chat_messages?: TestScenarioChatMessage[];
  user_notes?: TestScenarioUserNote[];
  actions?: TestScenarioAction[];
  /**
   * Coaching Phase Videos: between-session Break rows the user has
   * accumulated. Open breaks (no `ended_at`) drive `on_break=true`.
   */
  breaks?: TestScenarioBreak[];
}

export type TestScenario = {
  id: string;
  name: string;
  description: string;
  template: TestScenarioTemplate;
};
