import { Gender } from "@/enums/appearance/gender";
import { SkinTone } from "@/enums/appearance/skinTone";
import { HairColor } from "@/enums/appearance/hairColor";
import { EyeColor } from "@/enums/appearance/eyeColor";
import { Height } from "@/enums/appearance/height";
import { Build } from "@/enums/appearance/build";
import { AgeRange } from "@/enums/appearance/ageRange";

/**
 * Represents user appearance preferences for image generation.
 * These settings are stored on the User model and apply to all identity image generations.
 * All fields are optional, allowing users to set preferences incrementally.
 */
export interface UserAppearance {
  /** Gender preference for image generation */
  gender?: Gender | null;
  /** Skin tone preference following Apple emoji convention */
  skin_tone?: SkinTone | null;
  /** Hair color preference */
  hair_color?: HairColor | null;
  /** Eye color preference */
  eye_color?: EyeColor | null;
  /** Height preference */
  height?: Height | null;
  /** Build/body type preference */
  build?: Build | null;
  /** Age range preference */
  age_range?: AgeRange | null;
}
