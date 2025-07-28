import { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";

interface OptimizedImageProps {
  src: string;
  alt: string;
  className?: string;
  width?: number;
  height?: number;
  loading?: "lazy" | "eager";
  priority?: boolean;
  quality?: number;
  placeholder?: "blur" | "empty";
  blurDataURL?: string;
}

export function OptimizedImage({
  src,
  alt,
  className,
  width,
  height,
  loading = "lazy",
  priority = false,
  quality = 80,
  placeholder = "empty",
  blurDataURL
}: OptimizedImageProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (priority || loading === "eager") {
      setIsInView(true);
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { rootMargin: "50px" }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [priority, loading]);

  // Preload critical images
  useEffect(() => {
    if (priority) {
      const link = document.createElement("link");
      link.rel = "preload";
      link.as = "image";
      link.href = src;
      document.head.appendChild(link);
    }
  }, [src, priority]);

  const handleLoad = () => {
    setIsLoading(false);
  };

  const handleError = () => {
    setIsLoading(false);
    setHasError(true);
  };

  // Generate responsive srcSet for better performance
  const generateSrcSet = (baseSrc: string) => {
    if (!width) return undefined;
    
    const sizes = [1, 1.5, 2];
    return sizes
      .map(size => `${baseSrc}?w=${Math.round(width * size)}&q=${quality} ${size}x`)
      .join(", ");
  };

  return (
    <div 
      ref={imgRef}
      className={cn(
        "relative overflow-hidden",
        isLoading && placeholder === "blur" && "animate-pulse bg-muted",
        className
      )}
      style={{ width, height }}
    >
      {hasError ? (
        <div className="flex items-center justify-center w-full h-full bg-muted text-muted-foreground">
          <span className="text-sm">Failed to load image</span>
        </div>
      ) : (
        <>
          {/* Blur placeholder */}
          {isLoading && placeholder === "blur" && blurDataURL && (
            <img
              src={blurDataURL}
              alt=""
              className="absolute inset-0 w-full h-full object-cover filter blur-sm"
              aria-hidden="true"
            />
          )}
          
          {/* Main image */}
          {isInView && (
            <img
              src={src}
              srcSet={generateSrcSet(src)}
              alt={alt}
              width={width}
              height={height}
              loading={loading}
              onLoad={handleLoad}
              onError={handleError}
              className={cn(
                "w-full h-full object-cover transition-opacity duration-300",
                isLoading ? "opacity-0" : "opacity-100"
              )}
              sizes={width ? `(max-width: 768px) 100vw, ${width}px` : "100vw"}
            />
          )}
        </>
      )}
    </div>
  );
}

// Hook for image preloading
export function useImagePreloader(imageSrcs: string[]) {
  useEffect(() => {
    const preloadImages = imageSrcs.map(src => {
      const img = new Image();
      img.src = src;
      return img;
    });

    return () => {
      preloadImages.forEach(img => {
        img.src = "";
      });
    };
  }, [imageSrcs]);
}