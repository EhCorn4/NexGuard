import { QueryClient, QueryFunction } from "@tanstack/react-query";

async function throwIfResNotOk(res: Response) {
  if (!res.ok) {
    const text = (await res.text()) || res.statusText;
    throw new Error(`${res.status}: ${text}`);
  }
}

export async function apiRequest(
  method: string,
  url: string,
  data?: unknown | undefined,
): Promise<Response> {
  const res = await fetch(url, {
    method,
    headers: data ? { "Content-Type": "application/json" } : {},
    body: data ? JSON.stringify(data) : undefined,
    credentials: "include",
  });

  await throwIfResNotOk(res);
  return res;
}

type UnauthorizedBehavior = "returnNull" | "throw";
export const getQueryFn: <T>(options: {
  on401: UnauthorizedBehavior;
}) => QueryFunction<T> =
  ({ on401: unauthorizedBehavior }) =>
  async ({ queryKey }) => {
    // Construct URL from queryKey array
    let url: string;
    if (Array.isArray(queryKey) && queryKey.length > 1) {
      // Handle array-based queryKeys like ['/api/servers', guildId, 'config']
      url = queryKey.join('/');
    } else {
      // Handle simple string queryKeys
      url = queryKey[0] as string;
    }
    
    console.log('Query URL:', url);
    
    const res = await fetch(url, {
      credentials: "include",
    });

    if (unauthorizedBehavior === "returnNull" && res.status === 401) {
      return null;
    }

    await throwIfResNotOk(res);
    return await res.json();
  };

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      queryFn: getQueryFn({ on401: "throw" }),
      refetchInterval: false,
      refetchOnWindowFocus: false,
      staleTime: 1000 * 60 * 5, // 5 minutes for better performance
      gcTime: 1000 * 60 * 10, // 10 minutes in memory (formerly cacheTime)
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors, but retry on network issues
        if (error?.message?.includes('4')) {
          return false;
        }
        return failureCount < 2; // Limit retries to prevent slowdown
      },
      retryDelay: (attemptIndex) => Math.min(1000 * Math.pow(2, attemptIndex), 5000),
    },
    mutations: {
      retry: 1, // Retry mutations once on failure
      retryDelay: 1000,
    },
  },
});

// Prefetch critical data on app start
export function prefetchCriticalData() {
  // Bot status - most important for homepage
  queryClient.prefetchQuery({
    queryKey: ["/api/bot/status"],
    staleTime: 30 * 1000, // Fresh data every 30 seconds
  });
  
  // Features data - static content
  queryClient.prefetchQuery({
    queryKey: ["/api/features"],
    staleTime: 10 * 60 * 1000, // 10 minutes for mostly static content
  });
  
  // Config data
  queryClient.prefetchQuery({
    queryKey: ["/api/config"],
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
