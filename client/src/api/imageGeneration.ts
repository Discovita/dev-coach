import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";
import {
  GenerateImageRequest,
  GenerateImageResponse,
  SaveImageRequest,
  SaveImageResponse,
} from "@/types/imageGeneration";

/**
 * Image Generation API
 * --------------------
 * Functions for generating identity images using Gemini AI.
 * Uses the image generation types from @/types/imageGeneration.
 *
 * Endpoints covered (see backend AdminIdentityViewSet):
 * - generateIdentityImage:    POST   /api/v1/admin/identities/generate-image/
 * - saveGeneratedImage:       POST   /api/v1/admin/identities/save-generated-image/
 */

/**
 * Generate an identity image using Gemini.
 * POST /api/v1/admin/identities/generate-image/
 * @param request - Generation request with identity_id, user_id, optional additional_prompt and save_to_identity
 * @returns GenerateImageResponse with base64 image and optionally updated identity
 */
export async function generateIdentityImage(
  request: GenerateImageRequest
): Promise<GenerateImageResponse> {
  const response = await authFetch(
    `${COACH_BASE_URL}/admin/identities/generate-image`,
    {
      method: "POST",
      body: JSON.stringify(request),
    }
  );
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Failed to generate image" }));
    throw new Error(error.error || "Failed to generate image");
  }
  return response.json();
}

/**
 * Save a previously generated image to an identity.
 * POST /api/v1/admin/identities/save-generated-image/
 * @param request - Save request with identity_id and image_base64
 * @returns SaveImageResponse with updated identity
 */
export async function saveGeneratedImage(
  request: SaveImageRequest
): Promise<SaveImageResponse> {
  const response = await authFetch(
    `${COACH_BASE_URL}/admin/identities/save-generated-image`,
    {
      method: "POST",
      body: JSON.stringify(request),
    }
  );
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Failed to save image" }));
    throw new Error(error.error || "Failed to save image");
  }
  return response.json();
}

