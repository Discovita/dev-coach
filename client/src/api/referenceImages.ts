import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";
import {
  ReferenceImage,
  CreateReferenceImageRequest,
  UpdateReferenceImageRequest,
} from "@/types/referenceImage";

/**
 * Reference Images API
 * -------------------
 * Functions for managing reference images (user-uploaded photos for AI generation).
 * Uses the ReferenceImage type from @/types/referenceImage.
 *
 * Endpoints covered (see backend ReferenceImageViewSet):
 * - listReferenceImages:     GET    /api/v1/reference-images/?user_id={uuid}
 * - getReferenceImage:        GET    /api/v1/reference-images/{id}/
 * - createReferenceImage:     POST   /api/v1/reference-images/
 * - updateReferenceImage:     PATCH  /api/v1/reference-images/{id}/
 * - deleteReferenceImage:     DELETE /api/v1/reference-images/{id}/
 * - uploadReferenceImage:    POST   /api/v1/reference-images/{id}/upload-image/
 */

/**
 * List reference images for a user.
 * GET /api/v1/reference-images/?user_id={uuid}
 * @param userId - Optional user ID (admin only). If not provided, returns current user's images.
 * @returns Array of ReferenceImage objects.
 */
export async function listReferenceImages(
  userId?: string
): Promise<ReferenceImage[]> {
  const url = userId
    ? `${COACH_BASE_URL}/reference-images?user_id=${userId}`
    : `${COACH_BASE_URL}/reference-images`;
  const response = await authFetch(url, {
    method: "GET",
  });
  if (!response.ok) {
    throw new Error("Failed to fetch reference images");
  }
  return response.json();
}

/**
 * Get a single reference image by ID.
 * GET /api/v1/reference-images/{id}/
 * @param id - The UUID of the reference image to fetch.
 * @returns ReferenceImage object.
 */
export async function getReferenceImage(id: string): Promise<ReferenceImage> {
  const url = `${COACH_BASE_URL}/reference-images/${id}`;
  const response = await authFetch(url, {
    method: "GET",
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch reference image ${id}`);
  }
  return response.json();
}

/**
 * Create a new reference image.
 * POST /api/v1/reference-images/
 * @param data - Reference image data (name, order, optional user_id for admin)
 * @param imageFile - Optional image file to upload
 * @returns Created ReferenceImage object.
 */
export async function createReferenceImage(
  data: CreateReferenceImageRequest,
  imageFile?: File
): Promise<ReferenceImage> {
  const formData = new FormData();
  
  if (data.name) formData.append("name", data.name);
  if (data.order !== undefined) formData.append("order", data.order.toString());
  if (data.user_id) formData.append("user_id", data.user_id);
  if (imageFile) formData.append("image", imageFile);

  const response = await authFetch(`${COACH_BASE_URL}/reference-images`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Failed to create reference image" }));
    throw new Error(error.error || "Failed to create reference image");
  }
  return response.json();
}

/**
 * Update a reference image.
 * PATCH /api/v1/reference-images/{id}/
 * @param id - The UUID of the reference image to update.
 * @param data - Updated reference image data (name, order)
 * @returns Updated ReferenceImage object.
 */
export async function updateReferenceImage(
  id: string,
  data: UpdateReferenceImageRequest
): Promise<ReferenceImage> {
  const response = await authFetch(`${COACH_BASE_URL}/reference-images/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Failed to update reference image ${id}`);
  }
  return response.json();
}

/**
 * Delete a reference image.
 * DELETE /api/v1/reference-images/{id}/
 * @param id - The UUID of the reference image to delete.
 */
export async function deleteReferenceImage(id: string): Promise<void> {
  const response = await authFetch(`${COACH_BASE_URL}/reference-images/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error(`Failed to delete reference image ${id}`);
  }
}

/**
 * Upload or replace the image file for a reference image.
 * POST /api/v1/reference-images/{id}/upload-image/
 * @param id - The UUID of the reference image.
 * @param imageFile - The image file to upload.
 * @returns Updated ReferenceImage object with new image URLs.
 */
export async function uploadReferenceImage(
  id: string,
  imageFile: File
): Promise<ReferenceImage> {
  const formData = new FormData();
  formData.append("image", imageFile);

  const response = await authFetch(
    `${COACH_BASE_URL}/reference-images/${id}/upload-image`,
    {
      method: "POST",
      body: formData,
    }
  );
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Failed to upload image" }));
    throw new Error(error.error || "Failed to upload image");
  }
  return response.json();
}

