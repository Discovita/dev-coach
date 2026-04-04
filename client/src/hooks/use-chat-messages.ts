import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchChatMessages, resetChatMessages } from "@/api/user";
import { fetchTestScenarioChatMessages } from "@/api/testScenarioUser";
import { apiClient } from "@/api/coach";
import { useUserTarget } from "@/context/UserTargetContext";
import { CoachResponse } from "@/types/coachResponse";
import { CoachRequest } from "@/types/coachRequest";
import { Message } from "@/types/message";
import { ComponentConfig } from "@/types/componentConfig";
import { makeComponentDisplayOnly } from "@/utils/componentConfig";

/**
 * useChatMessages hook
 * Handles fetching and updating chat messages using TanStack Query.
 *
 * Context-aware: reads from UserTargetContext to determine query key prefix,
 * which API endpoint to fetch from, and which send function to use.
 * When inside a UserTargetProvider, operates on the impersonated user's data
 * via admin endpoints.
 *
 * The reset mutation is only available in non-impersonating mode.
 * Test scenario resets go through a separate flow (ConversationResetter).
 *
 * Used in: ChatInterface, ConversationResetter, and any component that
 * needs to read or update chat messages.
 */
export function useChatMessages() {
  const { isImpersonating, targetUserId, queryKeyPrefix } = useUserTarget();
  const queryClient = useQueryClient();

  const chatMessagesKey = [...queryKeyPrefix, "chatMessages"];
  const componentConfigKey = [...queryKeyPrefix, "componentConfig"];

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: chatMessagesKey,
    queryFn: isImpersonating
      ? () => fetchTestScenarioChatMessages(targetUserId!)
      : fetchChatMessages,
    enabled: isImpersonating ? !!targetUserId : true,
    staleTime: 1000 * 60 * 10,
    retry: false,
  });

  const { data: componentConfig } = useQuery({
    queryKey: componentConfigKey,
    queryFn: () => null,
    enabled: isImpersonating ? !!targetUserId : true,
  });

  /**
   * Mutation for sending a chat message.
   * In impersonating mode, uses sendTestScenarioMessage and includes user_id.
   */
  const updateMutation = useMutation({
    mutationFn: async (request: CoachRequest) => {
      if (isImpersonating) {
        return apiClient.sendTestScenarioMessage({
          ...request,
          user_id: targetUserId!,
        });
      }
      return apiClient.sendMessage(request);
    },
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: chatMessagesKey });

      const componentConfigFromCache =
        queryClient.getQueryData<ComponentConfig | null>(componentConfigKey);

      if (componentConfigFromCache) {
        queryClient.setQueryData<Message[] | undefined>(
          chatMessagesKey,
          (old) => {
            const current = old ?? [];
            let lastCoachIndex = -1;
            for (let i = current.length - 1; i >= 0; i--) {
              if (current[i].role === "coach") {
                lastCoachIndex = i;
                break;
              }
            }
            if (lastCoachIndex === -1) return current;
            return current.map((msg, idx) => {
              if (idx === lastCoachIndex) {
                return {
                  ...msg,
                  component_config:
                    makeComponentDisplayOnly(componentConfigFromCache) ??
                    undefined,
                };
              }
              return msg;
            });
          }
        );
        queryClient.setQueryData(componentConfigKey, null);
      }
    },
    onSuccess: (response: CoachResponse, variables) => {
      console.log("[useChatMessages] Response:", response);
      queryClient.cancelQueries({ queryKey: chatMessagesKey });

      queryClient.setQueryData<Message[] | undefined>(
        chatMessagesKey,
        (old) => {
          const current = old ?? [];
          const userMsg: Message = {
            role: "user",
            content: variables.message,
            timestamp: new Date().toISOString(),
          };
          const coachMsg: Message | null = response.message
            ? {
                role: "coach",
                content: response.message,
                timestamp: new Date().toISOString(),
              }
            : null;

          const last = current[current.length - 1];
          const hasUserAlready =
            !!last &&
            last.role === "user" &&
            last.content === variables.message;

          const next: Message[] = hasUserAlready
            ? [...current]
            : [...current, userMsg];

          if (response.component) {
            console.log(
              "[useChatMessages] Component response detected, invalidating chat messages to get persistent components"
            );
            queryClient.invalidateQueries({ queryKey: chatMessagesKey });
          }

          return coachMsg ? [...next, coachMsg] : next;
        }
      );

      if (response.final_prompt !== undefined) {
        queryClient.setQueryData(
          [...queryKeyPrefix, "finalPrompt"],
          response.final_prompt
        );
      }

      queryClient.setQueryData(componentConfigKey, response.component || null);

      queryClient.invalidateQueries({
        queryKey: [...queryKeyPrefix, "actions"],
      });
      queryClient.invalidateQueries({
        queryKey: [...queryKeyPrefix, "coachState"],
      });
      queryClient.invalidateQueries({
        queryKey: [...queryKeyPrefix, "identities"],
      });
    },
  });

  /**
   * Reset mutation — only available for the logged-in user (non-impersonating).
   * Test scenario resets are handled by ConversationResetter via useResetTestScenario.
   */
  const resetMutation = useMutation({
    mutationFn: async () => {
      return resetChatMessages();
    },
    onSuccess: (newHistory) => {
      queryClient.setQueryData(chatMessagesKey, newHistory);
      queryClient.invalidateQueries({
        queryKey: [...queryKeyPrefix, "coachState"],
      });
      queryClient.invalidateQueries({
        queryKey: [...queryKeyPrefix, "finalPrompt"],
      });
      queryClient.invalidateQueries({
        queryKey: [...queryKeyPrefix, "actions"],
      });
      queryClient.invalidateQueries({
        queryKey: [...queryKeyPrefix, "identities"],
      });
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
    pendingMessage: updateMutation.variables,
    isPending: updateMutation.status === "pending",
    isUpdateError: updateMutation.isError,
    /**
     * Reset all chat messages for the logged-in user.
     * Not available in impersonating mode — test scenario resets
     * go through useResetTestScenario instead.
     */
    resetChatMessages: resetMutation.mutateAsync,
    resetStatus: resetMutation.status,
  };
}
