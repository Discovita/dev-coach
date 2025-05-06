/**
 * Prompts API
 * ----------
 * Functions for fetching and managing prompts from the backend.
 * Uses the Prompt and PromptCreate types from @/types/prompt.
 *
 * Endpoints covered (see backend PromptViewSet):
 * - fetchAllPrompts:        GET    /api/prompts/
 * - fetchPromptById:        GET    /api/prompts/{id}/
 * - createPrompt:           POST   /api/prompts/
 * - updatePrompt:           PUT    /api/prompts/{id}/
 * - partialUpdatePrompt:    PATCH  /api/prompts/{id}/
 * - deletePrompt:           DELETE /api/prompts/{id}/
 */
import { COACH_BASE_URL } from "@/constants/api";
import { Prompt, PromptCreate } from "@/types/prompt";

/**
 * Fetch all prompts from the backend.
 * GET /api/prompts/
 * Returns: Array of Prompt objects.
 * Used by: usePrompts hook, PromptsTabs, etc.
 */
export async function fetchAllPrompts(): Promise<Prompt[]> {
  const url = `${COACH_BASE_URL}/prompts`;
  const response = await fetch(url, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  if (!response.ok) {
    throw new Error("Failed to fetch prompts");
  }
  return response.json();
}

/**
 * Fetch a single prompt by ID.
 * GET /api/prompts/{id}/
 * @param id - The UUID of the prompt to fetch.
 * Returns: Prompt object.
 */
export async function fetchPromptById(id: string): Promise<Prompt> {
  const url = `${COACH_BASE_URL}/prompts/${id}`;
  const response = await fetch(url, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch prompt with id ${id}`);
  }
  return response.json();
}

/**
 * Create a new prompt.
 * POST /api/prompts/
 * @param data - PromptCreate object (fields for new prompt)
 * Returns: Created Prompt object.
 */
export async function createPrompt(data: PromptCreate): Promise<Prompt> {
  const url = `${COACH_BASE_URL}/prompts`;
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error("Failed to create prompt");
  }
  return response.json();
}

/**
 * Update a prompt (full update).
 * PUT /api/prompts/{id}/
 * @param id - The UUID of the prompt to update.
 * @param data - Prompt object (all fields required)
 * Returns: Updated Prompt object.
 */
export async function updatePrompt(id: string, data: Prompt): Promise<Prompt> {
  const url = `${COACH_BASE_URL}/prompts/${id}`;
  const response = await fetch(url, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Failed to update prompt with id ${id}`);
  }
  return response.json();
}

/**
 * Partially update a prompt.
 * PATCH /api/prompts/{id}/
 * @param id - The UUID of the prompt to update.
 * @param data - Partial Prompt object (only fields to update)
 * Returns: Updated Prompt object.
 */
export async function partialUpdatePrompt(
  id: string,
  data: Partial<Prompt>
): Promise<Prompt> {
  const url = `${COACH_BASE_URL}/prompts/${id}`;
  const response = await fetch(url, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Failed to partially update prompt with id ${id}`);
  }
  return response.json();
}

/**
 * Delete a prompt.
 * DELETE /api/prompts/{id}/
 * @param id - The UUID of the prompt to delete.
 * Returns: void (throws on error)
 */
export async function deletePrompt(id: string): Promise<void> {
  const url = `${COACH_BASE_URL}/prompts/${id}`;
  const response = await fetch(url, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
  });
  if (!response.ok) {
    throw new Error(`Failed to delete prompt with id ${id}`);
  }
}

/**
 * Soft delete a prompt (set is_active to false).
 * POST /api/prompts/{id}/soft_delete/
 * @param id - The UUID of the prompt to soft delete.
 * Returns: Updated Prompt object with is_active: false.
 */
export async function softDeletePrompt(id: string): Promise<Prompt> {
  const url = `${COACH_BASE_URL}/prompts/${id}/soft_delete`;
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!response.ok) {
    throw new Error(`Failed to soft delete prompt with id ${id}`);
  }
  return response.json();
}
