import { useQuery } from "@tanstack/react-query";

export function useAuth() {
  const { data: user, isLoading, error } = useQuery({
    queryKey: ["/api/auth/user"],
    retry: false,
    staleTime: Infinity, // Never consider stale
    gcTime: Infinity, // Keep in cache forever
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    refetchOnReconnect: false,
    refetchInterval: false,
  });

  return {
    user,
    isLoading,
    isAuthenticated: !!user && !error,
  };
}