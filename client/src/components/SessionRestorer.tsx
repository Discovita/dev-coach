import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { fetchUserComplete } from "@/api/user";
import { getCookie } from "@/api/auth";
import { User } from "@/types/user";

/**
 * This component restores the user session by checking for an access token in cookies and fetching
 * the user data if the token is present. It essentially auto logs in the user if they have cookies
 * present.
 */

export function SessionRestorer() {
  const queryClient = useQueryClient();
  console.log("[SessionRestorer] Rendering...");

  useEffect(() => {
    const profile = queryClient.getQueryData<User>(["user", "profile"]);
    if (!profile) {
      console.log(
        "[SessionRestorer] No user profile in cache, checking cookies..."
      );
      const accessToken = getCookie("discovita-access-token");
      if (accessToken) {
        console.log(
          "[SessionRestorer] Access token found in cookies, fetching user data..."
        );
        fetchUserComplete().then((user) => {
          if (user) {
            // Set all cache keys as in setUserDataInCache
            queryClient.setQueryData(["user", "profile"], {
              id: user.id,
              email: user.email,
              first_name: user.first_name,
              last_name: user.last_name,
              is_active: user.is_active,
              is_superuser: user.is_superuser,
              is_staff: user.is_staff,
              last_login: user.last_login,
              created_at: user.created_at,
              updated_at: user.updated_at,
              groups: user.groups,
              user_permissions: user.user_permissions,
            });
            queryClient.setQueryData(["user", "coachState"], user.coach_state);
            queryClient.setQueryData(["user", "identities"], user.identities);
            queryClient.setQueryData(
              ["user", "chatMessages"],
              user.chat_messages
            );
            queryClient.setQueryData(["user", "complete"], user);
            queryClient.setQueryData(["user", "isAdmin"], !!user.is_staff);
          }
        });
      }
    } else {
      console.log("[SessionRestorer] User profile already in cache.");
    }
  }, [queryClient]);

  return null;
}
