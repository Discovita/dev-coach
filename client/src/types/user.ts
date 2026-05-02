import type { Identity } from "./identity";
import type { CoachState } from "./coachState";
import type { Message } from "./message";
import type { Gender } from "@/enums/appearance/gender";
import type { SkinTone } from "@/enums/appearance/skinTone";
import type { HairColor } from "@/enums/appearance/hairColor";
import type { EyeColor } from "@/enums/appearance/eyeColor";
import type { Height } from "@/enums/appearance/height";
import type { Build } from "@/enums/appearance/build";
import type { AgeRange } from "@/enums/appearance/ageRange";

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
  
  // Appearance fields for image generation
  gender?: Gender | null;
  skin_tone?: SkinTone | null;
  hair_color?: HairColor | null;
  eye_color?: EyeColor | null;
  height?: Height | null;
  build?: Build | null;
  age_range?: AgeRange | null;
}
