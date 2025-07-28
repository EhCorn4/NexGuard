import { useState, useEffect, useMemo } from "react";
import { compress, decompress } from "lz-string";

interface CompressionWrapperProps {
  data: any;
  children: (compressedData: any, compressionRatio: number) => React.ReactNode;
  enableCompression?: boolean;
}

export function CompressionWrapper({ 
  data, 
  children, 
  enableCompression = true 
}: CompressionWrapperProps) {
  const [compressionStats, setCompressionStats] = useState({
    originalSize: 0,
    compressedSize: 0,
    ratio: 1
  });

  const processedData = useMemo(() => {
    if (!enableCompression || !data) return data;

    try {
      const originalString = JSON.stringify(data);
      const originalSize = new Blob([originalString]).size;
      
      const compressed = compress(originalString);
      const compressedSize = new Blob([compressed]).size;
      
      const ratio = compressedSize / originalSize;
      
      setCompressionStats({
        originalSize,
        compressedSize, 
        ratio
      });

      // Return decompressed data for use
      return JSON.parse(decompress(compressed) || originalString);
    } catch (error) {
      console.warn('Compression failed, using original data:', error);
      return data;
    }
  }, [data, enableCompression]);

  return (
    <div>
      {children(processedData, compressionStats.ratio)}
      {process.env.NODE_ENV === 'development' && enableCompression && (
        <div className="fixed bottom-4 right-4 bg-black/80 text-white p-2 rounded text-xs">
          Compression: {(compressionStats.ratio * 100).toFixed(1)}% 
          ({compressionStats.compressedSize}B / {compressionStats.originalSize}B)
        </div>
      )}
    </div>
  );
}

// Hook for automatic data compression in components
export function useDataCompression<T>(data: T, enabled = true): T {
  return useMemo(() => {
    if (!enabled || !data) return data;
    
    try {
      const compressed = compress(JSON.stringify(data));
      const decompressed = decompress(compressed);
      return JSON.parse(decompressed || JSON.stringify(data));
    } catch {
      return data;
    }
  }, [data, enabled]);
}