# User Appearance Type

The `UserAppearance` interface represents user appearance preferences for image generation. These settings are stored on the User model and apply to all identity image generations.

## Location

`client/src/types/userAppearance.ts`

## Interface Definition

```typescript
interface UserAppearance {
  gender?: Gender | null;
  skin_tone?: SkinTone | null;
  hair_color?: HairColor | null;
  eye_color?: EyeColor | null;
  height?: Height | null;
  build?: Build | null;
  age_range?: AgeRange | null;
}
```

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `gender` | `Gender \| null` | Gender preference for image generation (man, woman, person) |
| `skin_tone` | `SkinTone \| null` | Skin tone preference following Apple emoji convention |
| `hair_color` | `HairColor \| null` | Hair color preference |
| `eye_color` | `EyeColor \| null` | Eye color preference |
| `height` | `Height \| null` | Height preference |
| `build` | `Build \| null` | Build/body type preference |
| `age_range` | `AgeRange \| null` | Age range preference |

## Usage

All fields are optional, allowing users to set preferences incrementally. The appearance preferences are used when generating identity images to customize how the user is visualized.

## Related Enums

- `Gender` - `client/src/enums/appearance/gender.ts`
- `SkinTone` - `client/src/enums/appearance/skinTone.ts`
- `HairColor` - `client/src/enums/appearance/hairColor.ts`
- `EyeColor` - `client/src/enums/appearance/eyeColor.ts`
- `Height` - `client/src/enums/appearance/height.ts`
- `Build` - `client/src/enums/appearance/build.ts`
- `AgeRange` - `client/src/enums/appearance/ageRange.ts`

## Backend Model

These fields correspond to the User model in `server/apps/users/models/user.py`.
