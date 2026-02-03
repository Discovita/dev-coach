import { Identity } from "./identity";

/**
 * Request payload for generating an identity image.
 */
export interface GenerateImageRequest {
  /** UUID of the identity to generate image for */
  identity_id: string;
  /** UUID of the user (for reference images) */
  user_id: string;
  /** Extra instructions (optional) */
  additional_prompt?: string;
  /** Whether to save directly to identity (default: false) */
  save_to_identity?: boolean;
}

/**
 * Response from image generation endpoint.
 */
export interface GenerateImageResponse {
  /** Whether generation was successful */
  success: boolean;
  /** Base64 encoded image data */
  image_base64: string;
  /** Updated identity (if save_to_identity was true) */
  identity?: Identity;
  /** Error message (if success is false) */
  error?: string;
}

/**
 * Request payload for saving a generated image to an identity.
 */
export interface SaveImageRequest {
  /** UUID of the identity */
  identity_id: string;
  /** Base64 encoded image data */
  image_base64: string;
}

/**
 * Response from save image endpoint.
 */
export interface SaveImageResponse {
  /** Whether save was successful */
  success: boolean;
  /** Updated identity with image */
  identity: Identity;
  /** Error message (if success is false) */
  error?: string;
}

/**
 * Request payload for starting a new image chat session.
 */
export interface StartImageChatRequest {
  /** UUID of the identity to generate image for */
  identity_id: string;
  /** UUID of the user (for admin endpoints only) */
  user_id?: string;
  /** Extra instructions (optional) */
  additional_prompt?: string;
}

/**
 * Response from start image chat endpoint.
 */
export interface StartImageChatResponse {
  /** Base64 encoded image data */
  image_base64: string;
  /** UUID of the identity */
  identity_id: string;
  /** Name of the identity */
  identity_name: string;
}

/**
 * Request payload for continuing an image chat session.
 */
export interface ContinueImageChatRequest {
  /** UUID of the user (for admin endpoints only) */
  user_id?: string;
  /** Edit instruction */
  edit_prompt: string;
}

/**
 * Response from continue image chat endpoint.
 */
export interface ContinueImageChatResponse {
  /** Base64 encoded image data */
  image_base64: string;
  /** UUID of the identity */
  identity_id: string;
  /** Name of the identity */
  identity_name: string;
}

