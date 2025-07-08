import { motion, AnimatePresence } from "framer-motion";
import { ReactNode } from "react";

interface PageTransitionProps {
  children: ReactNode;
  className?: string;
}

const pageVariants = {
  initial: {
    opacity: 0,
    y: 20,
    scale: 0.98
  },
  in: {
    opacity: 1,
    y: 0,
    scale: 1
  },
  out: {
    opacity: 0,
    y: -20,
    scale: 1.02
  }
};

const pageTransition = {
  type: "tween",
  ease: "anticipate",
  duration: 0.4
};

export function PageTransition({ children, className = "" }: PageTransitionProps) {
  return (
    <motion.div
      initial="initial"
      animate="in"
      exit="out"
      variants={pageVariants}
      transition={pageTransition}
      className={className}
    >
      {children}
    </motion.div>
  );
}

export function FadeTransition({ children, className = "" }: PageTransitionProps) {
  const fadeVariants = {
    initial: { opacity: 0 },
    in: { opacity: 1 },
    out: { opacity: 0 }
  };

  const fadeTransition = {
    duration: 0.3,
    ease: "easeInOut"
  };

  return (
    <motion.div
      initial="initial"
      animate="in"
      exit="out"
      variants={fadeVariants}
      transition={fadeTransition}
      className={className}
    >
      {children}
    </motion.div>
  );
}

export function SlideTransition({ children, className = "", direction = "right" }: PageTransitionProps & { direction?: "left" | "right" | "up" | "down" }) {
  const getSlideVariants = () => {
    const distance = 50;
    switch (direction) {
      case "left":
        return {
          initial: { opacity: 0, x: -distance },
          in: { opacity: 1, x: 0 },
          out: { opacity: 0, x: distance }
        };
      case "right":
        return {
          initial: { opacity: 0, x: distance },
          in: { opacity: 1, x: 0 },
          out: { opacity: 0, x: -distance }
        };
      case "up":
        return {
          initial: { opacity: 0, y: -distance },
          in: { opacity: 1, y: 0 },
          out: { opacity: 0, y: distance }
        };
      case "down":
        return {
          initial: { opacity: 0, y: distance },
          in: { opacity: 1, y: 0 },
          out: { opacity: 0, y: -distance }
        };
      default:
        return {
          initial: { opacity: 0, x: distance },
          in: { opacity: 1, x: 0 },
          out: { opacity: 0, x: -distance }
        };
    }
  };

  const slideTransition = {
    type: "tween",
    ease: "easeInOut",
    duration: 0.35
  };

  return (
    <motion.div
      initial="initial"
      animate="in"
      exit="out"
      variants={getSlideVariants()}
      transition={slideTransition}
      className={className}
    >
      {children}
    </motion.div>
  );
}