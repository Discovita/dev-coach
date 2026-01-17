# Scene Inputs Type

The `SceneInputs` interface represents scene-specific inputs for identity image generation. These fields are stored on the Identity model and vary per identity.

## Location

`client/src/types/sceneInputs.ts`

## Interface Definition

```typescript
interface SceneInputs {
  clothing?: string | null;
  mood?: string | null;
  setting?: string | null;
}
```

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `clothing` | `string \| null` | What the person is wearing in this identity visualization (e.g., 'linen button-down shirt') |
| `mood` | `string \| null` | Emotional state/feeling in this identity visualization (e.g., 'proud and calm') |
| `setting` | `string \| null` | Environment/location for this identity visualization (e.g., 'on a hill overlooking the ocean') |

## Usage

All fields are optional text inputs that describe the scene for visualization. These values are specific to each identity and are used when generating images for that identity.

## Related Types

- `Identity` - `client/src/types/identity.ts` (includes these fields)

## Backend Model

These fields correspond to the Identity model in `server/apps/identities/models.py`.
