import { Identity } from "./identity";
import { CoachState } from "./coachState";
import { Message } from "./message";

export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  is_active?: boolean;
  is_superuser?: boolean;
  is_staff?: boolean;
  last_login?: string | null;
  created_at: string;
  updated_at: string;
  groups?: number[];
  user_permissions?: number[];
  identities?: Identity[];
  coach_state?: CoachState;
  chat_messages?: Message[];
  /** Appearance preferences for image generation (optional) */
  gender?: string | null;
  skin_tone?: string | null;
  hair_color?: string | null;
  eye_color?: string | null;
  height?: string | null;
  build?: string | null;
  age_range?: string | null;
}
