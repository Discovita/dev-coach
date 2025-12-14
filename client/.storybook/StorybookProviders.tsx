import React, { useMemo } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '../src/providers/ThemeProvider';
import type { User } from '../src/types/user';
import { Toaster as Sonner } from 'sonner';

type StorybookProvidersProps = {
  children: React.ReactNode;
  /**
   * Optional override for the authenticated user to pre-populate in TanStack Query cache.
   * - When omitted (undefined): a generic user is provided
   * - When null: no user is set, allowing testing of unauthenticated states
   * - When provided: that user is used, allowing testing of admin, regular user, etc.
   */
  mockUser?: User | null;
  /**
   * Optional theme override for Storybook.
   * Defaults to "light" theme.
   */
  defaultTheme?: string;
};

const createDefaultUser = (): User => {
  const now = new Date().toISOString();
  return {
    id: 'storybook-user',
    email: 'storybook-user@example.com',
    first_name: 'Storybook',
    last_name: 'User',
    is_active: true,
    is_superuser: false,
    is_staff: false,
    last_login: now,
    created_at: now,
    updated_at: now,
    groups: [],
    user_permissions: [],
  };
};

const createQueryClient = (mockUser?: User | null) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  });

  // Pre-populate query cache with mock user data if provided
  // This allows components using useProfile() to have data available immediately
  // If mockUser is explicitly null, leave cache empty to test unauthenticated states
  if (mockUser !== undefined && mockUser !== null) {
    queryClient.setQueryData(['user', 'profile'], {
      id: mockUser.id,
      email: mockUser.email,
      first_name: mockUser.first_name,
      last_name: mockUser.last_name,
      is_active: mockUser.is_active,
      is_superuser: mockUser.is_superuser,
      is_staff: mockUser.is_staff,
      last_login: mockUser.last_login,
      created_at: mockUser.created_at,
      updated_at: mockUser.updated_at,
      groups: mockUser.groups,
      user_permissions: mockUser.user_permissions,
    });
    queryClient.setQueryData(['user', 'isAdmin'], !!mockUser.is_staff);
    
    // Optionally set other user-related data if provided
    if (mockUser.coach_state) {
      queryClient.setQueryData(['user', 'coachState'], mockUser.coach_state);
    }
    if (mockUser.identities) {
      queryClient.setQueryData(['user', 'identities'], mockUser.identities);
    }
    if (mockUser.chat_messages) {
      queryClient.setQueryData(['user', 'chatMessages'], mockUser.chat_messages);
    }
    if (mockUser) {
      queryClient.setQueryData(['user', 'complete'], mockUser);
    }
  }

  return queryClient;
};

/**
 * StorybookProviders
 * 
 * Provides all necessary context providers for Storybook stories.
 * Matches the app structure from main.tsx:
 * - QueryClientProvider with retry disabled for predictable testing
 * - ThemeProvider for theme support
 * - BrowserRouter for routing
 * - Sonner Toaster for notifications
 * 
 * Optionally pre-populates TanStack Query cache with mock user data,
 * allowing components using useProfile() and useIsAdmin() to work immediately.
 * 
 * MSW handlers can be used in stories to intercept HTTP requests made by TanStack Query hooks.
 * 
 * Usage in stories:
 * ```tsx
 * export default {
 *   decorators: [
 *     (Story) => (
 *       <StorybookProviders mockUser={adminUser}>
 *         <Story />
 *       </StorybookProviders>
 *     ),
 *   ],
 * };
 * ```
 */
export const StorybookProviders: React.FC<StorybookProvidersProps> = ({
  children,
  mockUser,
  defaultTheme = 'light',
}) => {
  // Only create default user if mockUser is undefined (not provided)
  // If mockUser is explicitly null, we want to test unauthenticated state
  const userToUse = useMemo(() => {
    if (mockUser === undefined) {
      return createDefaultUser();
    }
    return mockUser;
  }, [mockUser]);
  
  const queryClient = useMemo(() => createQueryClient(userToUse), [userToUse]);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ThemeProvider defaultTheme={defaultTheme}>
          {children}
          <Sonner closeButton richColors position="top-right" />
        </ThemeProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

