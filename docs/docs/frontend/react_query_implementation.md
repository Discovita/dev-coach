# React Query Implementation Guide

## Overview

This document describes how we use TanStack Query (React Query) in this project for data fetching, caching, and state management. The approach is simple and pragmatic, focusing on clear separation of concerns and maintainability.

## Architecture

We use a three-layer architecture:

### 1. **API Layer** (`client/src/api/`)

- Contains pure functions for HTTP requests (e.g., `fetchAllPrompts`, `fetchEnums`).
- Each function corresponds to a backend endpoint.
- No caching or React Query logic here.
- Example:  
  ```typescript
  // client/src/api/prompts.ts
  export async function fetchAllPrompts(): Promise<Prompt[]> { ... }
  ```

### 2. **Query Layer** (`client/src/hooks/`)

- Contains custom hooks that wrap API functions with React Query.
- Hooks use `useQuery` for fetching and caching.
- Query keys are simple arrays (e.g., `["prompts", "all"]`).
- Hooks set sensible defaults for `staleTime` and `retry`.
- Example:
  ```typescript
  // client/src/hooks/use-prompts.ts
  export function usePrompts() {
    return useQuery<Prompt[]>({
      queryKey: ["prompts", "all"],
      queryFn: fetchAllPrompts,
      staleTime: 1000 * 60 * 10, // 10 minutes
      retry: false,
    });
  }
  ```

### 3. **Component Layer** (`client/src/pages/`)

- Components use the custom hooks to fetch and display data.
- Components handle loading, error, and empty states.
- Mutations (create, update, delete) are called directly via API functions.
- After a mutation, components call `refetch` on the relevant query hook to update the cache.
- Example:
  ```typescript
  // client/src/pages/prompts/Prompts.tsx
  const { data: allPrompts, refetch: refetchPrompts } = usePrompts();
  // ...
  await createPrompt(data);
  await refetchPrompts();
  ```

## Query Key Management

- Query keys are defined inline as arrays (e.g., `["prompts", "all"]`, `["core", "enums"]`).
- No centralized query key constants/types.
- Query keys are kept simple and descriptive.

## Cache Management

- We rely on React Query's built-in caching.
- After mutations, we call `refetch` on the relevant query to update the cache.
- No optimistic updates or manual cache manipulation.
- No use of `useMutation` for mutations; all mutations are handled via direct API calls.

## Error and Loading States

- Each hook returns `isLoading`, `isError`, and `refetch`.
- Components display loading indicators or error messages as needed.

## Enums and Dropdowns

- Enums for dropdowns (coach states, allowed actions, context keys) are fetched via `useCoreEnums`.
- Used to populate select/multiselect components in forms.

## Example Usage

### Fetching Prompts

```typescript
import { usePrompts } from "@/hooks/use-prompts";

const { data: prompts, isLoading, isError, refetch } = usePrompts();
```

### Creating a Prompt

```typescript
import { createPrompt } from "@/api/prompts";
import { usePrompts } from "@/hooks/use-prompts";

const { refetch } = usePrompts();

await createPrompt(data);
await refetch();
```

### Fetching Enums

```typescript
import { useCoreEnums } from "@/hooks/use-core";

const { data: enums, isLoading } = useCoreEnums();
```

## Best Practices

- Use custom hooks for all data fetching.
- Always call `refetch` after a mutation to keep data up to date.
- Handle loading and error states in components.
- Keep query keys simple and descriptive.
- Use enums from the backend to populate dropdowns and selects.

## Further Reading

- [TanStack Query Documentation](https://tanstack.com/query/latest)
