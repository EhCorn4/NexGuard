import { useEffect } from "react";
import { queryClient } from "@/lib/queryClient";

// Cache prefetching for critical data
export function usePrefetchCriticalData() {
  useEffect(() => {
    // Prefetch bot status - most critical data
    queryClient.prefetchQuery({
      queryKey: ["/api/bot/status"],
      staleTime: 30 * 1000, // 30 seconds
    });

    // Prefetch features data
    queryClient.prefetchQuery({
      queryKey: ["/api/features"],
      staleTime: 5 * 60 * 1000, // 5 minutes
    });

    // Prefetch developers data
    queryClient.prefetchQuery({
      queryKey: ["/api/developers"],
      staleTime: 10 * 60 * 1000, // 10 minutes
    });
  }, []);
}

// Component for prefetching on hover
interface PrefetchOnHoverProps {
  children: React.ReactNode;
  queryKey: string[];
  enabled?: boolean;
}

export function PrefetchOnHover({ children, queryKey, enabled = true }: PrefetchOnHoverProps) {
  const handleMouseEnter = () => {
    if (enabled) {
      queryClient.prefetchQuery({
        queryKey,
        staleTime: 2 * 60 * 1000, // 2 minutes
      });
    }
  };

  return (
    <div onMouseEnter={handleMouseEnter}>
      {children}
    </div>
  );
}

// Service Worker registration for caching
export function useServiceWorker() {
  useEffect(() => {
    if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
          .then((registration) => {
            console.log('SW registered: ', registration);
          })
          .catch((registrationError) => {
            console.log('SW registration failed: ', registrationError);
          });
      });
    }
  }, []);
}

// Memory cleanup for better performance
export function useMemoryOptimization() {
  useEffect(() => {
    const cleanup = () => {
      // Clear old query cache entries
      queryClient.getQueryCache().clear();
      
      // Force garbage collection in development
      if (process.env.NODE_ENV === 'development' && 'gc' in window) {
        (window as any).gc();
      }
    };

    // Cleanup on page visibility change
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'hidden') {
        cleanup();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);
}