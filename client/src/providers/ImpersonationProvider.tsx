import React, { useState, useCallback, useMemo } from "react";
import {
  ImpersonationContext,
  type ImpersonatedUser,
  type ImpersonationContextValue,
} from "@/context/ImpersonationContext";

/**
 * ImpersonationProvider
 *
 * Wraps the authenticated app shell to provide global admin impersonation state.
 * When an admin starts impersonating a user, all child components that read from
 * UserTargetContext (via the UserTargetProvider wired in the authenticated layout)
 * will automatically switch to fetching the impersonated user's data.
 *
 * Usage:
 *   <ImpersonationProvider>
 *     <AuthLayout>...</AuthLayout>
 *   </ImpersonationProvider>
 */
export const ImpersonationProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [impersonatedUser, setImpersonatedUser] =
    useState<ImpersonatedUser | null>(null);

  const startImpersonating = useCallback((user: ImpersonatedUser) => {
    setImpersonatedUser(user);
  }, []);

  const stopImpersonating = useCallback(() => {
    setImpersonatedUser(null);
  }, []);

  const value = useMemo<ImpersonationContextValue>(
    () => ({
      impersonatedUser,
      startImpersonating,
      stopImpersonating,
    }),
    [impersonatedUser, startImpersonating, stopImpersonating]
  );

  return (
    <ImpersonationContext.Provider value={value}>
      {children}
    </ImpersonationContext.Provider>
  );
};
