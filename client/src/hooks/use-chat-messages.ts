import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchChatMessages, resetChatMessages } from "@/api/user";
import { apiClient } from "@/api/coach";
import { CoachResponse } from "@/types/coachResponse";
import { CoachRequest } from "@/types/coachRequest";
import { Message } from "@/types/message";

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
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["user", "chatMessages"],
    queryFn: fetchChatMessages,
  });

  // Get the current component config (set by mutations)
  const { data: componentConfig } = useQuery({
    queryKey: ["user", "componentConfig"],
    queryFn: () => null, // This will be set by mutations
  });

  /**
   * Mutation for sending a chat message to the backend.
   * Accepts a CoachRequest object with message, model_name, and optional actions.
   * On success, updates the chatMessages, identities, and coachState caches.
   */
  const updateMutation = useMutation({
    // mutationFn sends the message to the backend
    mutationFn: async (request: CoachRequest) => {
      return apiClient.sendMessage(request);
    },
    // On success, update all relevant caches with the response
    onSuccess: (response: CoachResponse, variables) => {
      // Append user (dedup) and coach messages to cache without invalidating messages
      queryClient.setQueryData<Message[] | undefined>(
        ["user", "chatMessages"],
        (old) => {
          const current = old ?? [];
          const last = current[current.length - 1];
          const hasUserAlready =
            !!last && last.role === "user" && last.content === variables.message;

          const maybeUserAppended = hasUserAlready
            ? current
            : [
                ...current,
                {
                  role: "user",
                  content: variables.message,
                  timestamp: new Date().toISOString(),
                } as Message,
              ];

          const maybeCoachAppended = response.message
            ? [
                ...maybeUserAppended,
                {
                  role: "coach",
                  content: response.message,
                  timestamp: new Date().toISOString(),
                } as Message,
              ]
            : maybeUserAppended;

          return maybeCoachAppended;
        }
      );

      if (response.final_prompt !== undefined) {
        queryClient.setQueryData(["user", "finalPrompt"], response.final_prompt);
      }

      // Handle component config - ALWAYS set it (even if null)
      queryClient.setQueryData(
        ["user", "componentConfig"],
        response.component || null
      );
    },
  });

  /**
   * Mutation for resetting (deleting) all chat messages for the user.
   * Step-by-step:
   * 1. Calls the resetChatMessages API function (POST /user/me/reset-chat-messages/).
   * 2. On success, updates the chatMessages cache with the new (empty or re-initialized) history.
   * 3. Invalidates coachState, finalPrompt, actions, and identities queries to ensure all related state is reset in the UI.
   * 4. Expose mutation function and status for UI consumption.
   */
  const resetMutation = useMutation({
    mutationFn: async () => {
      return resetChatMessages();
    },
    onSuccess: (newHistory) => {
      // 1. Update the chatMessages cache with the new (empty or re-initialized) history
      queryClient.setQueryData(["user", "chatMessages"], newHistory);
      // 2. Invalidate coachState so it is refetched/reset in the UI
      queryClient.invalidateQueries({ queryKey: ["user", "coachState"] });
      // 3. Invalidate finalPrompt so it is cleared or refetched
      queryClient.invalidateQueries({ queryKey: ["user", "finalPrompt"] });
      // 4. Invalidate actions so the actions history is cleared or refetched
      queryClient.invalidateQueries({ queryKey: ["user", "actions"] });
      // 5. Invalidate identities so the identities list is cleared or refetched
      queryClient.invalidateQueries({ queryKey: ["user", "identities"] });
    },
  });

  return {
    chatMessages: data,
    componentConfig,
    isLoading,
    isError,
    refetchChatMessages: refetch,
    updateChatMessages: updateMutation.mutateAsync,
    updateStatus: updateMutation.status,
    // Expose mutation state for optimistic UI
    pendingMessage: updateMutation.variables, // The message being sent (if any)
    isPending: updateMutation.status === "pending",
    isUpdateError: updateMutation.isError,
    /**
     * Reset all chat messages for the user.
     * Use: await resetChatMessagesFn();
     * Status: resetStatus
     */
    resetChatMessages: resetMutation.mutateAsync,
    resetStatus: resetMutation.status,
  };
}
