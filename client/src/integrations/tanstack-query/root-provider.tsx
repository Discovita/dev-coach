import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

let queryClientSingleton: QueryClient | null = null;

export function getContext() {
  if (!queryClientSingleton) {
    queryClientSingleton = new QueryClient({
      defaultOptions: {
        queries: {
          gcTime: 48 * 60 * 60 * 1000, // 48 hours
          staleTime: 1 * 60 * 60 * 1000, // 1 hour
        },
      },
    });
  }
  return {
    queryClient: queryClientSingleton,
  }
}

export function Provider({
  children,
  queryClient,
}: {
  children: React.ReactNode
  queryClient: QueryClient
}) {
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}
