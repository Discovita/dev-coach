import { useProfile } from "@/hooks/use-profile";

/**
 * useIsAdmin hook
 * Determines if the current user is an admin based on their profile.
 * Uses useProfile to get profile data and derives isAdmin from is_staff field.
 *
 * Returns: boolean | undefined (undefined while loading or if no profile)
 *
 * Used in: Any component that needs to check if the current user is an admin.
 */
export function useIsAdmin(): boolean | undefined {
  const { profile } = useProfile();
  return profile?.is_staff ?? undefined;
}

