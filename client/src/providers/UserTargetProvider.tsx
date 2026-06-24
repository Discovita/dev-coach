import {
	UserTargetContext,
	type UserTargetContextValue,
} from "@/context/UserTargetContext";
import type React from "react";
import { useMemo } from "react";

interface UserTargetProviderProps {
	targetUserId: string | undefined;
	scenarioId: string | undefined;
	children: React.ReactNode;
}

/**
 * Wraps a component subtree so that all hooks inside automatically
 * switch to admin/test-user endpoints and scoped query keys.
 *
 * Usage:
 *   <UserTargetProvider targetUserId={testUserId} scenarioId={scenario.id}>
 *     <ChatInterface />
 *     <CoachStateVisualizer />
 *   </UserTargetProvider>
 *
 * Ported from: dev-coach/client/src/providers/UserTargetProvider.tsx
 */
export const UserTargetProvider: React.FC<UserTargetProviderProps> = ({
	targetUserId,
	scenarioId,
	children,
}) => {
	const value = useMemo<UserTargetContextValue>(() => {
		if (targetUserId) {
			return {
				isImpersonating: true,
				targetUserId,
				scenarioId: scenarioId ?? null,
				queryKeyPrefix: ["testScenarioUser", targetUserId],
			};
		}
		return {
			isImpersonating: false,
			targetUserId: null,
			scenarioId: null,
			queryKeyPrefix: ["user"],
		};
	}, [targetUserId, scenarioId]);

	return (
		<UserTargetContext.Provider value={value}>
			{children}
		</UserTargetContext.Provider>
	);
};
