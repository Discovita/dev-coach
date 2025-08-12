import { CoachingPhase } from "@/enums/coachingPhase";
import { IdentityCategory } from "@/enums/identityCategory";
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
}

export interface TestScenarioIdentity {
  name: string;
  category: IdentityCategory;
  affirmation?: string;
  visualization?: string;
  notes?: string[];
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
}

export type TestScenario = {
  id: string;
  name: string;
  description: string;
  template: TestScenarioTemplate;
};
