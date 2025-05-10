import { CoachState } from "./coachState";
import { Identity } from "./identity";
import { Message } from "./message";

export interface CoachResponse {
  message: string;
  coach_state: CoachState;
  final_prompt?: string;
  actions?: string[];
  chat_history?: Message[];
  identities?: Identity[];
}
