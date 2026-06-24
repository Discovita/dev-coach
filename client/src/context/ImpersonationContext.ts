import { createContext, useContext } from "react";

/**
 * ImpersonationContext
 *
 * Global state for admin user impersonation. When an admin selects a user
 * to "view as", their ID and basic info are stored here. The authenticated
 * layout reads this context to wrap all pages in a UserTargetProvider,
 * causing all data hooks to fetch the impersonated user's data instead.
 *
 * Consumed by: _authenticated/route.tsx, ImpersonationBanner, AuthLayout
 * Provided by: ImpersonationProvider (wraps the authenticated layout)
 */

export interface ImpersonatedUser {
	id: string;
	email: string;
	first_name: string;
	last_name: string;
}

export interface ImpersonationContextValue {
	impersonatedUser: ImpersonatedUser | null;
	startImpersonating: (user: ImpersonatedUser) => void;
	stopImpersonating: () => void;
}

const defaultValue: ImpersonationContextValue = {
	impersonatedUser: null,
	startImpersonating: () => {},
	stopImpersonating: () => {},
};

export const ImpersonationContext =
	createContext<ImpersonationContextValue>(defaultValue);

/**
 * Hook to consume the ImpersonationContext.
 * Safe to call outside a provider — returns default (no impersonation) value.
 */
export function useImpersonation(): ImpersonationContextValue {
	return useContext(ImpersonationContext);
}
