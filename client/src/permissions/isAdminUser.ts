import type { User } from "@/types/user";

/**
 * Determines whether a user has admin-level access.
 *
 * Mirrors the backend's IsAdminUser permission class
 * (server/permissions/is_admin_user.py) which grants access when
 * is_staff OR is_superuser is true.
 *
 * This is the single source of truth for admin checks on the frontend.
 * Use this instead of inline is_staff checks everywhere.
 */
export function isAdminUser(user: User | undefined | null): boolean {
  if (!user) return false;
  return Boolean(user.is_staff || user.is_superuser);
}
