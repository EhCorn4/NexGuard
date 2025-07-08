import { memo, Suspense, lazy } from "react";
import { ErrorBoundary } from "@/components/ui/error-boundary";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";

interface PerformanceWrapperProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  skeletonType?: "card" | "list" | "grid";
  skeletonCount?: number;
}

export const PerformanceWrapper = memo(function PerformanceWrapper({
  children,
  fallback,
  skeletonType = "card",
  skeletonCount = 3
}: PerformanceWrapperProps) {
  const defaultFallback = fallback || <LoadingSkeleton type={skeletonType} count={skeletonCount} />;

  return (
    <ErrorBoundary>
      <Suspense fallback={defaultFallback}>
        {children}
      </Suspense>
    </ErrorBoundary>
  );
});