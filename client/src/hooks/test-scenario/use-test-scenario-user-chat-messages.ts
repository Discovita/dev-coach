import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchTestScenarioUserChatMessages } from "@/api/testScenarioUser";
import { sendTestScenarioUserMessage } from "@/api/coach";
import { CoachResponse } from "@/types/coachResponse";

/**
 * useTestScenarioUserChatMessages
 * Handles fetching and updating a test scenario user's chat messages using TanStack Query.
 * Implements optimistic UI and mutation logic similar to useChatMessages.
 *
 * @param userId - The id of the test scenario user
 */
export function useTestScenarioUserChatMessages(userId: string) {
  const queryClient = useQueryClient();

  // Fetch the test user's chat messages
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["testScenarioUser", userId, "chatMessages"],
    queryFn: () => fetchTestScenarioUserChatMessages(userId),
    enabled: !!userId,
    staleTime: 1000 * 60 * 10,
    retry: false,
  });

  /**
   * Mutation for sending a chat message as the test scenario user.
   * Accepts an object with content (string) and optional model (string).
   * On success, updates the chatMessages, identities, and coachState caches for the test user.
   */
  const updateMutation = useMutation({
    mutationFn: async ({ content, model }: { content: string; model?: string }) => {
      return sendTestScenarioUserMessage(userId, content, model);
    },
    onSuccess: (response: CoachResponse) => {
      // Update all relevant caches for the test user
      if (response.chat_history) {
        queryClient.setQueryData(
          ["testScenarioUser", userId, "chatMessages"],
          response.chat_history
        );
      }
      if (response.identities) {
        queryClient.setQueryData(["testScenarioUser", userId, "identities"], response.identities);
      }
      if (response.coach_state) {
        queryClient.setQueryData(["testScenarioUser", userId, "coachState"], response.coach_state);
      }
      if (response.final_prompt !== undefined) {
        queryClient.setQueryData(
          ["testScenarioUser", userId, "finalPrompt"],
          response.final_prompt
        );
      }
      // Invalidate actions cache to trigger refetch of latest actions from database
      queryClient.invalidateQueries({ queryKey: ["testScenarioUser", userId, "actions"] });
    },
  });

  return {
    chatMessages: data,
    isLoading,
    isError,
    refetchChatMessages: refetch,
    updateChatMessages: updateMutation.mutateAsync,
    updateStatus: updateMutation.status,
    pendingMessage: updateMutation.variables, // The message being sent (if any)
    isPending: updateMutation.status === "pending",
    isUpdateError: updateMutation.isError,
  };
} 