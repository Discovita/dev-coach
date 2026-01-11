import { ImageSizes } from "./imageSizes";

/**
 * Reference Image type matching backend ReferenceImageSerializer.
 * Used for storing user-uploaded photos for AI image generation.
 */
export interface ReferenceImage {
  /** Unique identifier */
  id: string;
  /** User ID this reference image belongs to */
  user: string;
  /** Optional name/label for this image */
  name: string;
  /** Display order (0-4) */
  order: number;
  /** Image URLs for different sizes (null if no image uploaded yet) */
  image: ImageSizes | null;
  /** Creation timestamp */
  created_at: string;
  /** Last update timestamp */
  updated_at: string;
}

/**
 * Request payload for creating a new reference image.
 */
export interface CreateReferenceImageRequest {
  /** Optional name/label */
  name?: string;
  /** Optional order (0-4), auto-assigned if not provided */
  order?: number;
  /** Optional user_id (admin only) */
  user_id?: string;
}

/**
 * Request payload for updating a reference image.
 */
export interface UpdateReferenceImageRequest {
  /** Optional name/label */
  name?: string;
  /** Optional order (0-4) */
  order?: number;
}

