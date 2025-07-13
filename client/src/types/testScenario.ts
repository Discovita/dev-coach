import { CoachingPhase } from "@/enums/coachingPhase";
import { IdentityCategory } from "@/enums/identityCategory";

export interface TestScenarioUser {
  first_name: string;
  last_name: string;
}

export interface TestScenarioCoachState {
  current_phase?: CoachingPhase;
  identity_focus?: IdentityCategory;
  skipped_identity_categories?: IdentityCategory[];
  who_you_are?: string[];
  who_you_want_to_be?: string[];
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

export interface TestScenarioTemplate {
  user: TestScenarioUser;
  coach_state?: TestScenarioCoachState;
  identities?: TestScenarioIdentity[];
  chat_messages?: TestScenarioChatMessage[];
  user_notes?: TestScenarioUserNote[];
}

export type TestScenario = {
  id: string;
  name: string;
  description: string;
  template: TestScenarioTemplate;
};
