import { Skeleton } from "@/components/ui/skeleton";

interface LoadingSkeletonProps {
  type?: "card" | "list" | "grid";
  count?: number;
}

export function LoadingSkeleton({ type = "card", count = 3 }: LoadingSkeletonProps) {
  const skeletons = Array.from({ length: count }, (_, i) => i);

  if (type === "card") {
    return (
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        {skeletons.map((i) => (
          <div key={i} className="space-y-4">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        ))}
      </div>
    );
  }

  if (type === "list") {
    return (
      <div className="space-y-4">
        {skeletons.map((i) => (
          <div key={i} className="flex items-center space-x-4">
            <Skeleton className="h-12 w-12 rounded-full" />
            <div className="space-y-2 flex-1">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-2/3" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {skeletons.map((i) => (
        <Skeleton key={i} className="h-24 w-full" />
      ))}
    </div>
  );
}