import { useState, useEffect } from "react";

export function useSimpleAuth() {
  const [authState, setAuthState] = useState({
    user: null,
    isLoading: true,
    error: null,
    isAuthenticated: false,
  });

  const checkAuth = async () => {
    try {
      console.log('Simple auth check starting...');
      setAuthState(prev => ({ ...prev, isLoading: true }));

      const response = await fetch('/api/auth/user', {
        credentials: 'include',
        headers: {
          'Cache-Control': 'no-cache',
        },
      });

      console.log('Simple auth response:', response.status);

      if (response.ok) {
        const user = await response.json();
        console.log('Simple auth success:', user);
        setAuthState({
          user,
          isLoading: false,
          error: null,
          isAuthenticated: true,
        });
      } else {
        console.log('Simple auth failed:', response.status);
        setAuthState({
          user: null,
          isLoading: false,
          error: null,
          isAuthenticated: false,
        });
      }
    } catch (error) {
      console.error('Simple auth error:', error);
      setAuthState({
        user: null,
        isLoading: false,
        error: error as any,
        isAuthenticated: false,
      });
    }
  };

  useEffect(() => {
    // Check auth on mount
    checkAuth();

    // Check for auth success parameter
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('auth') === 'success') {
      console.log('Auth success detected, rechecking...');
      // Clean URL
      window.history.replaceState({}, '', window.location.pathname);
      // Recheck auth after a delay
      setTimeout(checkAuth, 200);
    }
  }, []);

  return { ...authState, refetch: checkAuth };
}