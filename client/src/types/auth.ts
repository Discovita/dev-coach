import { User } from "@/types/User";

/**
 * Authentication Types
 * Defines all types related to authentication flows.
 * These types match the standardized backend responses.
 */

// Request Types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
}

export interface ResetPasswordCredentials {
  token: string;
  password: string;
}

/**
 * Standardized API Response Type
 * Matches backend response format:
 * - success: boolean flag for operation status
 * - message?: optional success message
 * - error?: optional error message
 * - user?: user data if applicable
 * - tokens?: auth tokens if applicable
 * - email_sent?: email verification status
 */
export interface AuthResponse {
  success: boolean;
  message?: string;
  error?: string;
  user?: User;
  tokens?: {
    access: string;
    refresh: string;
  };
  email_sent?: boolean;
}

/**
 * Auth Context Type
 * Defines the shape of our authentication context
 * Used in AuthContext.ts and consumed by useAuth.tsx
 */
export interface AuthContextType {
  user: User | null;
  isAdmin?: boolean;
  isLoading?: boolean;
  login: (userData: LoginCredentials) => Promise<AuthResponse>;
  register: (userData: RegisterCredentials) => Promise<AuthResponse>;
  forgotPassword: (email: string) => Promise<AuthResponse>;
  resetPassword: (data: ResetPasswordCredentials) => Promise<AuthResponse>;
  logout: () => void;
  setTestUser: (powerpathId: number, onProfileChange?: () => void) => void;
}

/**
 * Request Options Type
 * Used by authFetch utility for making authenticated requests
 */
export type RequestOptions = RequestInit & {
  headers?: Record<string, string>;
};
