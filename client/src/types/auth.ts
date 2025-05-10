/**
 * Authentication Types
 * Defines all types related to authentication flows.
 * These types match the standardized backend responses.
 */

import { User } from "@/types/user";

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

export interface AuthResponse {
  success: boolean;
  message?: string;
  error?: string;
  user_id?: string;
  tokens?: {
    access: string;
    refresh: string;
  };
  email_sent?: boolean;
  user?: User; // this can be added later
}

/**
 * Request Options Type
 * Used by authFetch utility for making authenticated requests
 */
export type RequestOptions = RequestInit & {
  headers?: Record<string, string>;
};
