import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  login as loginApi,
  register as registerApi,
  forgotPassword as forgotPasswordApi,
  resetPassword as resetPasswordApi,
  logout as logoutApi,
} from "@/api/auth";
import {
  RegisterCredentials,
  LoginCredentials,
  AuthResponse,
  ResetPasswordCredentials,
} from "@/types/auth";
import { User } from "@/types/user";

/**
 * useAuth hook
 * Handles only authentication state and actions using TanStack Query.
 * - Provides login, register, forgot/reset password, and logout actions.
 * - After login/register, sets user data in TanStack Query cache for instant access.
 * - Also sets isAdmin as its own query key for easy access across the app.
 * - No context/provider required.
 */
export function useAuth() {
  const queryClient = useQueryClient();

  // Helper to set user data in TanStack Query cache after login/register
  function setUserDataInCache(user: User) {
    // Set each piece of user data under its own query key
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
    queryClient.setQueryData(["user", "chatMessages"], user.chat_messages);
    queryClient.setQueryData(["user", "complete"], user);
    queryClient.setQueryData(["user", "isAdmin"], !!user.is_staff);
  }

  // Login mutation
  const loginMutation = useMutation<AuthResponse, unknown, LoginCredentials>({
    mutationFn: loginApi,
    onSuccess: (data) => {
      // If user data is returned, set it in the cache
      if (data && data.user) {
        setUserDataInCache(data.user);
      }
    },
  });

  // Register mutation
  const registerMutation = useMutation<
    AuthResponse,
    unknown,
    RegisterCredentials
  >({
    mutationFn: registerApi,
    onSuccess: (data) => {
      // If user data is returned, set it in the cache
      if (data && data.user) {
        setUserDataInCache(data.user);
      }
    },
  });

  // Forgot password mutation
  const forgotPasswordMutation = useMutation<AuthResponse, unknown, string>({
    mutationFn: forgotPasswordApi,
  });

  // Reset password mutation
  const resetPasswordMutation = useMutation<
    AuthResponse,
    unknown,
    ResetPasswordCredentials
  >({
    mutationFn: resetPasswordApi,
  });

  // Logout mutation
  const logoutMutation = useMutation<void, unknown, void>({
    mutationFn: logoutApi,
    onSuccess: () => {
      // Optionally, invalidate user/profile queries here if needed
      window.location.href = "/";
    },
  });

  return {
    login: loginMutation.mutateAsync,
    loginStatus: loginMutation.status,
    register: registerMutation.mutateAsync,
    registerStatus: registerMutation.status,
    forgotPassword: forgotPasswordMutation.mutateAsync,
    forgotPasswordStatus: forgotPasswordMutation.status,
    resetPassword: resetPasswordMutation.mutateAsync,
    resetPasswordStatus: resetPasswordMutation.status,
    logout: logoutMutation.mutateAsync,
    logoutStatus: logoutMutation.status,
  };
}
