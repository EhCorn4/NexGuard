import { useEffect } from 'react';
import { useLocation } from 'wouter';

export const useScrollToTop = () => {
  const [location] = useLocation();
  
  useEffect(() => {
    // Smooth scroll to top when location changes
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }, [location]);
};