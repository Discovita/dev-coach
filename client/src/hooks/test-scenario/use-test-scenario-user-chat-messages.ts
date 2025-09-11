import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchTestScenarioUserChatMessages } from "@/api/testScenarioUser";
import { sendTestScenarioUserMessage } from "@/api/coach";
import { CoachResponse } from "@/types/coachResponse";
import { Message } from "@/types/message";

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
    mutationFn: async ({
      content,
      model,
    }: {
      content: string;
      model?: string;
    }) => {
      return sendTestScenarioUserMessage(userId, content, model);
    },
    onSuccess: (response: CoachResponse, variables) => {
      console.log("[useTestScenarioUserChatMessages] onSuccess", response);
      // Ensure messages query doesn't refetch right now
      queryClient.cancelQueries({
        queryKey: ["testScenarioUser", userId, "chatMessages"],
      });

      // Append the user's message (if not already present) and the coach's reply
      queryClient.setQueryData<Message[] | undefined>(
        ["testScenarioUser", userId, "chatMessages"],
        (old) => {
          const current = old ?? [];
          const userMsg: Message = {
            role: "user",
            content: variables.content,
            timestamp: new Date().toISOString(),
          };
          const coachMsg: Message | null = response.message
            ? {
                role: "coach",
                content: response.message,
                timestamp: new Date().toISOString(),
              }
            : null;

          // Avoid duplicate user bubble if one already exists at the end (due to prior optimistic UI)
          const last = current[current.length - 1];
          const hasUserAlready =
            !!last && last.role === "user" && last.content === variables.content;

          const next: Message[] = hasUserAlready ? [...current] : [...current, userMsg];
          return coachMsg ? [...next, coachMsg] : next;
        }
      );

      // Append coach message to chat cache without invalidating to avoid flicker
      // (Handled together above)

      if (response.final_prompt !== undefined) {
        queryClient.setQueryData(
          ["testScenarioUser", userId, "finalPrompt"],
          response.final_prompt
        );
      }

      // Still refresh other test-user datasets, but keep messages stable
      queryClient.invalidateQueries({
        queryKey: ["testScenarioUser", userId, "actions"],
      });
      queryClient.invalidateQueries({
        queryKey: ["testScenarioUser", userId, "coachState"],
      });
      queryClient.invalidateQueries({
        queryKey: ["testScenarioUser", userId, "identities"],
      });
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
