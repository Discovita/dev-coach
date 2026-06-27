import { apiClient } from "@/api/coach";
import { fetchTestScenarioChatMessages } from "@/api/testScenarioUser";
import { fetchChatMessages, resetChatMessages } from "@/api/user";
import { useUserTarget } from "@/context/UserTargetContext";
import type { CoachRequest } from "@/types/coachRequest";
import type { CoachResponse } from "@/types/coachResponse";
import type { CoachState } from "@/types/coachState";
import type { ComponentConfig } from "@/types/componentConfig";
import type { Message } from "@/types/message";
import { makeComponentDisplayOnly } from "@/utils/componentConfig";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

/**
 * Monotonic id for client-created (optimistic/synthetic) messages. Stable
 * within a session and unique against server UUIDs, so a message row keeps the
 * same React key from its optimistic render through commit and never remounts
 * (a remount re-runs the row's entrance animation and makes the list flicker).
 * Resetting on reload is fine — keys only need to be unique within the live list.
 */
let clientMessageSeq = 0;
const nextClientMessageId = () => {
	clientMessageSeq += 1;
	return `client-${clientMessageSeq}`;
};

/**
 * Deliberate minimum "thinking" time before the coach's reply lands. The coach
 * dots show during this beat. Without it, canned-response turns (which skip the
 * LLM on the backend and return almost instantly) snap the reply in the same
 * breath as the user's message and feel robotic. Padding only affects fast
 * turns — slower LLM turns already exceed this.
 */
const MIN_THINKING_MS = 900;
const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

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
			const send = isImpersonating
				? apiClient.sendTestScenarioMessage({
						...request,
						user_id: targetUserId!,
					})
				: apiClient.sendMessage(request);
			// Hold a deliberate beat so the reply lands after the user's message,
			// not in the same instant. Promise.all resolves on the SLOWER of the
			// two, so this pads fast (canned) turns without delaying slow ones.
			const [response] = await Promise.all([send, sleep(MIN_THINKING_MS)]);
			return response;
		},
		onMutate: async (request: CoachRequest) => {
			await queryClient.cancelQueries({ queryKey: chatMessagesKey });

			// Snapshot the pre-mutation cache so onError can fully roll back the
			// optimistic writes below (the user bubble and the display-only freeze).
			const previousMessages =
				queryClient.getQueryData<Message[]>(chatMessagesKey);
			const previousComponentConfig =
				queryClient.getQueryData<ComponentConfig | null>(componentConfigKey);

			const componentConfigFromCache = previousComponentConfig;

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
					},
				);
				queryClient.setQueryData(componentConfigKey, null);
			}

			// Optimistically append the user's message with a STABLE client id, so
			// the bubble keeps the same React key from this paint through commit
			// (onSuccess keeps this same object — see `hasUserAlready` below).
			// `message: null` is a programmatic-only dispatch (e.g. the video
			// Continue button); the backend saves no user ChatMessage, so neither
			// do we.
			const now = Date.now();
			if (request.message !== null) {
				const optimisticUser: Message = {
					id: nextClientMessageId(),
					role: "user",
					content: request.message,
					timestamp: new Date(now).toISOString(),
				};
				queryClient.setQueryData<Message[] | undefined>(
					chatMessagesKey,
					(old) => [...(old ?? []), optimisticUser],
				);
			}

			// Append a PENDING coach placeholder — this is the loading-dots bubble.
			// onSuccess finalizes this exact message in place (same id), so the dots
			// crossfade into the response within one bubble rather than a separate
			// loading bubble unmounting. Timestamp is nudged +1ms so it always sorts
			// after the user message it answers.
			const pendingCoachId = nextClientMessageId();
			queryClient.setQueryData<Message[] | undefined>(
				chatMessagesKey,
				(old) => [
					...(old ?? []),
					{
						id: pendingCoachId,
						role: "coach",
						content: "",
						timestamp: new Date(now + 1).toISOString(),
						pending: true,
					},
				],
			);

			return { previousMessages, previousComponentConfig, pendingCoachId };
		},
		onError: (_error, _variables, context) => {
			// Roll the optimistic writes back to the pre-mutation snapshot so a
			// failed send doesn't leave a stranded user bubble or a prematurely
			// frozen (display-only) card.
			if (context) {
				queryClient.setQueryData(chatMessagesKey, context.previousMessages);
				queryClient.setQueryData(
					componentConfigKey,
					context.previousComponentConfig,
				);
			}
		},
		onSuccess: (response: CoachResponse, _variables, context) => {
			queryClient.cancelQueries({ queryKey: chatMessagesKey });

			queryClient.setQueryData<Message[] | undefined>(
				chatMessagesKey,
				(old) => {
					const current = old ?? [];
					const pendingId = context?.pendingCoachId;
					const hasText = !!response.message;
					// The component (if any) renders via `componentConfigKey` below,
					// so a component-only turn still has visible coach output.
					const hasComponent = !!response.component;

					// Finalize the pending coach placeholder IN PLACE (same id → same
					// React key) so the dots crossfade into the response within one
					// bubble. No new coach row is appended, nothing unmounts.
					if (pendingId) {
						if (!hasText && !hasComponent) {
							// No coach output this turn (e.g. the Identity Visualization
							// no-op phase) — drop the placeholder so there's no empty bubble.
							return current.filter((m) => m.id !== pendingId);
						}
						return current.map((m) =>
							m.id === pendingId
								? { ...m, content: response.message ?? "", pending: false }
								: m,
						);
					}

					// Fallback (no placeholder in context — shouldn't happen): append a
					// finalized coach message if there's output, otherwise leave as-is.
					if (!hasText && !hasComponent) return current;
					return [
						...current,
						{
							id: nextClientMessageId(),
							role: "coach",
							content: response.message ?? "",
							timestamp: new Date().toISOString(),
						},
					];
				},
			);

			if (response.component) {
				// Mark stale WITHOUT an active refetch (`refetchType: "none"`). The
				// component for this turn is already in `response.component` (the
				// backend always returns it — see process_message), and we set it
				// on `componentConfigKey` below, so the card renders without the
				// round-trip. Actively refetching here replaced the whole message
				// list with fresh server objects mid-turn, remounting every row
				// (new keys) and flashing the just-rendered card. Server truth
				// (DB ids, persisted component_config) reconciles on the next
				// natural mount instead.
				queryClient.invalidateQueries({
					queryKey: chatMessagesKey,
					refetchType: "none",
				});
			}

			if (response.final_prompt !== undefined) {
				queryClient.setQueryData(
					[...queryKeyPrefix, "finalPrompt"],
					response.final_prompt,
				);
			}

			queryClient.setQueryData(componentConfigKey, response.component || null);

			// Coaching Phase Videos (PR 15): mirror on_break from the coach
			// response into the coachState cache immediately so the composer
			// disables/enables this paint, not on the next refetch. The
			// coachState invalidation below refetches separately to confirm.
			if (response.on_break !== undefined) {
				queryClient.setQueryData<CoachState | undefined>(
					[...queryKeyPrefix, "coachState"],
					(old) => (old ? { ...old, on_break: response.on_break } : old),
				);
			}

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
