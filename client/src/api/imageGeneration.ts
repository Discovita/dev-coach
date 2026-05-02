import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";
import type {
  GenerateImageRequest,
  GenerateImageResponse,
  StartImageChatRequest,
  StartImageChatResponse,
  ContinueImageChatRequest,
  ContinueImageChatResponse,
  SaveImageRequest,
  SaveImageResponse,
  ImageGenerationErrorResponse,
} from "@/types/imageGeneration";
import { ImageGenerationError } from "@/types/imageGeneration";
import { createLogger, LogLevel } from "@/lib/logger";

const log = createLogger("imageGenerationApi", LogLevel.DEBUG);

/**
 * Image Generation API
 * --------------------
 * Functions for generating identity images using Gemini AI.
 * Uses the image generation types from @/types/imageGeneration.
 *
 * Endpoints covered:
 * - generateIdentityImage: POST /api/v1/admin/identities/generate-image/ (admin legacy)
 * - startImageChat:        POST /api/v1/identity-image-chat/start/ (public)
 *                          POST /api/v1/admin/identity-image-chat/start/ (admin, when user_id provided)
 * - continueImageChat:     POST /api/v1/identity-image-chat/continue/ (public)
 *                          POST /api/v1/admin/identity-image-chat/continue/ (admin, when user_id provided)
 * - saveGeneratedImage:         PATCH /api/v1/identities/{id}/upload-image/ (public)
 * - adminSaveGeneratedImage:    POST /api/v1/admin/identities/save-generated-image/ (admin, for impersonation)
 */

/**
 * Generate an identity image using Gemini (admin legacy endpoint).
 * POST /api/v1/admin/identities/generate-image/
 */
export async function generateIdentityImage(
  request: GenerateImageRequest
): Promise<GenerateImageResponse> {
  log.debug("Generating identity image (admin)", request);
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
  const data = await response.json();
  log.debug("Successfully generated identity image", { identity_id: data.identity?.id });
  return data;
}

/**
 * Start a new image generation chat session.
 * POST /api/v1/identity-image-chat/start/
 * @param request - Start chat request with identity_id and optional additional_prompt
 * @returns StartImageChatResponse with base64 image and identity info
 * @throws ImageGenerationError with detailed error info if generation fails
 */
export async function startImageChat(
  request: StartImageChatRequest
): Promise<StartImageChatResponse> {
  log.debug("Starting image chat", request);
  const endpoint = request.user_id
    ? `${COACH_BASE_URL}/admin/identity-image-chat/start`
    : `${COACH_BASE_URL}/identity-image-chat/start`;
  const response = await authFetch(
    endpoint,
    {
      method: "POST",
      body: JSON.stringify(request),
    }
  );
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ 
      error: "Failed to start image chat",
      error_code: "UNKNOWN",
      details: null,
    })) as ImageGenerationErrorResponse;
    
    log.error("Image chat start failed", errorData);
    throw new ImageGenerationError(errorData);
  }
  const data = await response.json();
  log.debug("Successfully started image chat", { identity_id: data.identity_id });
  return data;
}

/**
 * Continue an existing image chat session with an edit prompt.
 * POST /api/v1/identity-image-chat/continue/
 * @param request - Continue chat request with edit_prompt
 * @returns ContinueImageChatResponse with base64 image and identity info
 * @throws ImageGenerationError with detailed error info if edit fails
 */
export async function continueImageChat(
  request: ContinueImageChatRequest
): Promise<ContinueImageChatResponse> {
  log.debug("Continuing image chat", request);
  const endpoint = request.user_id
    ? `${COACH_BASE_URL}/admin/identity-image-chat/continue`
    : `${COACH_BASE_URL}/identity-image-chat/continue`;
  const response = await authFetch(
    endpoint,
    {
      method: "POST",
      body: JSON.stringify(request),
    }
  );
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ 
      error: "Failed to continue image chat",
      error_code: "UNKNOWN",
      details: null,
    })) as ImageGenerationErrorResponse;
    
    log.error("Image chat continue failed", errorData);
    throw new ImageGenerationError(errorData);
  }
  const data = await response.json();
  log.debug("Successfully continued image chat", { identity_id: data.identity_id });
  return data;
}

/**
 * Save a generated image to an identity (current user).
 * Converts base64 to a file and uploads via the user-scoped endpoint.
 * PATCH /api/v1/identities/{identity_id}/upload-image/
 * @param request - Save request with identity_id and image_base64
 * @returns SaveImageResponse with updated identity
 */
export async function saveGeneratedImage(
  request: SaveImageRequest
): Promise<SaveImageResponse> {
  log.debug("Saving generated image", { identity_id: request.identity_id });
  
  const base64Data = request.image_base64.replace(/^data:image\/\w+;base64,/, "");
  const byteCharacters = atob(base64Data);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  const blob = new Blob([byteArray], { type: "image/png" });
  
  const formData = new FormData();
  formData.append("image", blob, "generated-image.png");
  
  const response = await authFetch(
    `${COACH_BASE_URL}/identities/${request.identity_id}/upload-image`,
    {
      method: "PATCH",
      body: formData,
    }
  );
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Failed to save image" }));
    throw new Error(error.error || "Failed to save image");
  }
  const identity = await response.json();
  log.debug("Successfully saved generated image", { identity_id: identity.id });
  return {
    success: true,
    identity,
  };
}

/**
 * Save a generated image to an identity (admin endpoint).
 * Used when an admin is impersonating another user — the identity belongs
 * to a different user, so the user-scoped endpoint would 403.
 * POST /api/v1/admin/identities/save-generated-image/
 * @param request - Save request with identity_id and image_base64
 * @returns SaveImageResponse with updated identity
 */
export async function adminSaveGeneratedImage(
  request: SaveImageRequest
): Promise<SaveImageResponse> {
  log.debug("Saving generated image (admin)", { identity_id: request.identity_id });
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
