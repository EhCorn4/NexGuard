import { useEffect, useState } from "react";

interface PerformanceMetrics {
  pageLoadTime: number;
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  cumulativeLayoutShift: number;
  firstInputDelay: number;
  renderTime: number;
  apiResponseTime: number;
}

export function usePerformanceMonitor() {
  const [metrics, setMetrics] = useState<Partial<PerformanceMetrics>>({});

  useEffect(() => {
    // Web Vitals measurement
    const measureWebVitals = () => {
      // Core Web Vitals
      if ('web-vital' in window) {
        // This would integrate with actual web-vitals library
        // For now, we'll use Performance API
      }

      // Performance Observer for various metrics
      if ('PerformanceObserver' in window) {
        // Largest Contentful Paint
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lcp = entries[entries.length - 1];
          setMetrics(prev => ({ ...prev, largestContentfulPaint: lcp.startTime }));
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

        // First Input Delay
        const fidObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach(entry => {
            if (entry.name === 'first-input') {
              setMetrics(prev => ({ ...prev, firstInputDelay: entry.duration }));
            }
          });
        });
        fidObserver.observe({ entryTypes: ['first-input'] });

        return () => {
          lcpObserver.disconnect();
          fidObserver.disconnect();
        };
      }
    };

    // Navigation timing
    const measureNavigationTiming = () => {
      if ('performance' in window) {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        if (navigation) {
          setMetrics(prev => ({
            ...prev,
            pageLoadTime: navigation.loadEventEnd - navigation.fetchStart,
            firstContentfulPaint: navigation.domContentLoadedEventEnd - navigation.fetchStart
          }));
        }
      }
    };

    // Render performance measurement
    const measureRenderTime = () => {
      const startTime = performance.now();
      
      requestAnimationFrame(() => {
        const endTime = performance.now();
        setMetrics(prev => ({
          ...prev,
          renderTime: endTime - startTime
        }));
      });
    };

    measureWebVitals();
    measureNavigationTiming();
    measureRenderTime();

    // Measure API response times
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const start = performance.now();
      const response = await originalFetch(...args);
      const end = performance.now();
      
      setMetrics(prev => ({
        ...prev,
        apiResponseTime: end - start
      }));
      
      return response;
    };

    return () => {
      window.fetch = originalFetch;
    };
  }, []);

  return metrics;
}

// Performance monitoring component
export function PerformanceMonitor({ enabled = false }: { enabled?: boolean }) {
  const metrics = usePerformanceMonitor();

  if (!enabled || process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 bg-black/90 text-white p-3 rounded-lg text-xs font-mono z-50 max-w-xs">
      <div className="font-bold mb-2">Performance Metrics</div>
      {Object.entries(metrics).map(([key, value]) => (
        <div key={key} className="flex justify-between">
          <span className="capitalize">{key.replace(/([A-Z])/g, ' $1')}:</span>
          <span className={`ml-2 ${
            key.includes('Time') && value > 1000 ? 'text-red-400' :
            key.includes('Time') && value > 500 ? 'text-yellow-400' :
            'text-green-400'
          }`}>
            {typeof value === 'number' ? `${value.toFixed(1)}ms` : 'N/A'}
          </span>
        </div>
      ))}
    </div>
  );
}

// Bundle size analyzer
export function useBundleAnalyzer() {
  const [bundleInfo, setBundleInfo] = useState({
    chunkSizes: {} as Record<string, number>,
    totalSize: 0,
    loadedChunks: 0
  });

  useEffect(() => {
    // Analyze loaded chunks
    const analyzeChunks = () => {
      const scripts = document.querySelectorAll('script[src]');
      let totalSize = 0;
      const chunkSizes: Record<string, number> = {};

      scripts.forEach(script => {
        const src = script.getAttribute('src');
        if (src && src.includes('chunk')) {
          // Estimate chunk size (in production, this would use actual bundle analyzer data)
          const estimatedSize = Math.random() * 100000 + 10000; // Mock data
          chunkSizes[src] = estimatedSize;
          totalSize += estimatedSize;
        }
      });

      setBundleInfo({
        chunkSizes,
        totalSize,
        loadedChunks: Object.keys(chunkSizes).length
      });
    };

    analyzeChunks();

    // Re-analyze when new chunks are loaded
    const observer = new MutationObserver(analyzeChunks);
    observer.observe(document.head, { childList: true });

    return () => observer.disconnect();
  }, []);

  return bundleInfo;
}