import { motion } from "framer-motion";
import { ReactNode } from "react";

interface HoverScaleProps {
  children: ReactNode;
  className?: string;
  scale?: number;
  duration?: number;
}

export function HoverScale({ 
  children, 
  className = "", 
  scale = 1.02,
  duration = 0.2 
}: HoverScaleProps) {
  return (
    <motion.div
      className={className}
      whileHover={{ 
        scale,
        transition: { duration, ease: "easeOut" }
      }}
      whileTap={{ 
        scale: scale * 0.98,
        transition: { duration: 0.1 }
      }}
    >
      {children}
    </motion.div>
  );
}

interface FloatProps {
  children: ReactNode;
  className?: string;
  intensity?: number;
  duration?: number;
}

export function Float({ 
  children, 
  className = "",
  intensity = 5,
  duration = 3 
}: FloatProps) {
  return (
    <motion.div
      className={className}
      animate={{
        y: [-intensity, intensity, -intensity],
      }}
      transition={{
        duration,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    >
      {children}
    </motion.div>
  );
}