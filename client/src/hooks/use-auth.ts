import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  fetchUser,
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
import { User } from "@/types/User";

/**
 * useAuth hook
 * Handles all authentication state and actions using TanStack Query.
 * - Provides user, profile, isAdmin, isLoading, and all auth actions.
 * - No context/provider required.
 */
export function useAuth() {
  const queryClient = useQueryClient();

  // Query for current user and profile
  const {
    data: userData,
    isLoading,
    isError,
    refetch,
  } = useQuery<AuthResponse>({
    queryKey: ["auth", "user"],
    queryFn: fetchUser,
    retry: false,
  });

  // Helper to extract user and profile from response
  const user: User | null = userData?.user ?? null;
  const isAdmin: boolean = !!user?.is_staff;

  // Login mutation
  const loginMutation = useMutation<AuthResponse, unknown, LoginCredentials>({
    mutationFn: loginApi,
    onSuccess: (data) => {
      if (data.success) {
        queryClient.invalidateQueries({ queryKey: ["auth", "user"] });
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
      if (data.success) {
        queryClient.invalidateQueries({ queryKey: ["auth", "user"] });
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
      queryClient.removeQueries({ queryKey: ["auth", "user"] });
      // Optionally, redirect to login page here
      window.location.href = "/";
    },
  });

  return {
    user,
    isAdmin,
    isLoading,
    isError,
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
    refetchUser: refetch,
  };
}
