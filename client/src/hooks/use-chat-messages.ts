import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchChatMessages } from "@/api/user";
import { apiClient } from "@/api/coach";
import { CoachResponse } from "@/types/coachResponse";

/**
 * useChatMessages hook
 * Handles fetching and updating the user's chat messages using TanStack Query.
 *
 * Step-by-step:
 * 1. Fetch the user's chat messages from /user/me/chat-messages/ using fetchChatMessages.
 * 2. Expose loading, error, and data states for UI consumption.
 * 3. Provide a mutation for sending a new chat message to the backend.
 * 4. On success, update the chatMessages, identities, and coachState caches with the response.
 * 5. Invalidate or refetch as needed to keep data fresh.
 *
 * Used in: Any component that needs to read or update the user's chat messages.
 */
export function useChatMessages() {
  const queryClient = useQueryClient();

  // Fetch the user's chat messages
  const {
    data,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["user", "chatMessages"],
    queryFn: fetchChatMessages,
  });

  /**
   * Mutation for sending a chat message to the backend.
   * Accepts an object with content (string) and optional model (string).
   * On success, updates the chatMessages, identities, and coachState caches.
   */
  const updateMutation = useMutation({
    // mutationFn sends the message to the backend
    mutationFn: async ({ content, model }: { content: string; model?: string }) => {
      return apiClient.sendMessage(content, model ?? "");
    },
    // On success, update all relevant caches with the response
    onSuccess: (response: CoachResponse) => {
      if (response.chat_history) {
        queryClient.setQueryData(["user", "chatMessages"], response.chat_history);
      }
      if (response.identities) {
        queryClient.setQueryData(["user", "identities"], response.identities);
      }
      if (response.coach_state) {
        queryClient.setQueryData(["user", "coachState"], response.coach_state);
      }
    },
  });

  return {
    chatMessages: data,
    isLoading,
    isError,
    refetchChatMessages: refetch,
    updateChatMessages: updateMutation.mutateAsync,
    updateStatus: updateMutation.status,
  };
} 