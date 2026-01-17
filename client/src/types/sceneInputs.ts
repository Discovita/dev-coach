/**
 * Represents scene-specific inputs for identity image generation.
 * These fields are stored on the Identity model and vary per identity.
 * All fields are optional text inputs that describe the scene for visualization.
 */
export interface SceneInputs {
  /** What the person is wearing in this identity visualization (e.g., 'linen button-down shirt') */
  clothing?: string | null;
  /** Emotional state/feeling in this identity visualization (e.g., 'proud and calm') */
  mood?: string | null;
  /** Environment/location for this identity visualization (e.g., 'on a hill overlooking the ocean') */
  setting?: string | null;
}
