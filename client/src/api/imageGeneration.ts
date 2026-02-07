import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";
import {
  GenerateImageRequest,
  GenerateImageResponse,
  SaveImageRequest,
  SaveImageResponse,
  StartImageChatRequest,
  StartImageChatResponse,
  ContinueImageChatRequest,
  ContinueImageChatResponse,
  ImageGenerationError,
  ImageGenerationErrorResponse,
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

/**
 * Start a new image generation chat session.
 * Admin: POST /api/v1/admin/identity-image-chat/start/
 * Public: POST /api/v1/identity-image-chat/start/
 * @param request - Start chat request with identity_id, optional user_id (admin), optional additional_prompt
 * @returns StartImageChatResponse with base64 image and identity info
 * @throws ImageGenerationError with detailed error info if generation fails
 */
export async function startImageChat(
  request: StartImageChatRequest
): Promise<StartImageChatResponse> {
  // Use admin endpoint if user_id is provided, otherwise use public endpoint
  const endpoint = request.user_id
    ? `${COACH_BASE_URL}/admin/identity-image-chat/start`
    : `${COACH_BASE_URL}/identity-image-chat/start`;
  
  const response = await authFetch(endpoint, {
    method: "POST",
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ 
      error: "Failed to start image chat",
      error_code: "UNKNOWN",
      details: null,
    })) as ImageGenerationErrorResponse;
    
    throw new ImageGenerationError(errorData);
  }
  return response.json();
}

/**
 * Continue an existing image chat session with an edit prompt.
 * Admin: POST /api/v1/admin/identity-image-chat/continue/
 * Public: POST /api/v1/identity-image-chat/continue/
 * @param request - Continue chat request with edit_prompt, optional user_id (admin)
 * @returns ContinueImageChatResponse with base64 image and identity info
 * @throws ImageGenerationError with detailed error info if edit fails
 */
export async function continueImageChat(
  request: ContinueImageChatRequest
): Promise<ContinueImageChatResponse> {
  // Use admin endpoint if user_id is provided, otherwise use public endpoint
  const endpoint = request.user_id
    ? `${COACH_BASE_URL}/admin/identity-image-chat/continue`
    : `${COACH_BASE_URL}/identity-image-chat/continue`;
  
  const response = await authFetch(endpoint, {
    method: "POST",
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ 
      error: "Failed to continue image chat",
      error_code: "UNKNOWN",
      details: null,
    })) as ImageGenerationErrorResponse;
    
    throw new ImageGenerationError(errorData);
  }
  return response.json();
}

