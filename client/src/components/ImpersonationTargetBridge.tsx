import { useImpersonation } from "@/context/ImpersonationContext";
import { UserTargetProvider } from "@/providers/UserTargetProvider";
import type React from "react";

/**
 * ImpersonationTargetBridge
 *
 * Bridges the global ImpersonationContext into a UserTargetProvider.
 * When an admin is impersonating a user, this wraps children in a
 * UserTargetProvider so all data hooks automatically fetch the
 * impersonated user's data via admin endpoints.
 *
 * When not impersonating, children render without a UserTargetProvider,
 * so hooks use the default (logged-in user) behavior.
 *
 * Note: TestChat.tsx wraps with its own UserTargetProvider which overrides
 * this one (React context nesting), so test scenarios work independently.
 */
export const ImpersonationTargetBridge: React.FC<{
	children: React.ReactNode;
}> = ({ children }) => {
	const { impersonatedUser } = useImpersonation();

	if (impersonatedUser) {
		return (
			<UserTargetProvider
				targetUserId={impersonatedUser.id}
				scenarioId={undefined}
			>
				{children}
			</UserTargetProvider>
		);
	}

	return <>{children}</>;
};
