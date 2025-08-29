import { useState, useEffect } from "react";

// Global auth state that survives HMR
const AUTH_STORAGE_KEY = 'nexguard_auth_state';
const AUTH_TIMESTAMP_KEY = 'nexguard_auth_timestamp';

interface AuthState {
  user: any;
  isLoading: boolean;
  error: any;
  isAuthenticated: boolean;
}

// Singleton auth state to prevent multiple requests
class AuthManager {
  private static instance: AuthManager;
  private user: any = null;
  private isLoading = true;
  private error: any = null;
  private hasInitialized = false;
  private listeners: Array<() => void> = [];
  private promise: Promise<any> | null = null;
  private lastFetchTime = 0;
  private CACHE_DURATION = 60000; // 1 minute cache

  static getInstance() {
    if (!AuthManager.instance) {
      AuthManager.instance = new AuthManager();
      // Load cached state on creation
      AuthManager.instance.loadCachedState();
    }
    return AuthManager.instance;
  }

  private loadCachedState() {
    try {
      const cachedState = sessionStorage.getItem(AUTH_STORAGE_KEY);
      const timestamp = sessionStorage.getItem(AUTH_TIMESTAMP_KEY);
      
      if (cachedState && timestamp) {
        const cacheAge = Date.now() - parseInt(timestamp);
        if (cacheAge < this.CACHE_DURATION) {
          const state = JSON.parse(cachedState);
          this.user = state.user;
          this.error = state.error;
          this.isLoading = false;
          this.hasInitialized = true;
          this.lastFetchTime = parseInt(timestamp);
          console.log('Loaded cached auth state');
          return;
        }
      }
    } catch (e) {
      console.log('No valid cached auth state');
    }
  }

  private saveCachedState() {
    try {
      const state = {
        user: this.user,
        error: this.error,
      };
      sessionStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(state));
      sessionStorage.setItem(AUTH_TIMESTAMP_KEY, this.lastFetchTime.toString());
    } catch (e) {
      console.error('Failed to cache auth state');
    }
  }

  async fetchUser() {
    // Check if we have recent cached data
    const now = Date.now();
    if (this.hasInitialized && (now - this.lastFetchTime) < this.CACHE_DURATION) {
      console.log('Using cached auth data');
      return;
    }

    if (this.promise) {
      return this.promise; // Return existing promise if already fetching
    }

    this.promise = this.doFetch();
    return this.promise;
  }

  private async doFetch() {
    try {
      console.log('Fetching auth user');
      this.isLoading = true;
      this.lastFetchTime = Date.now();
      this.notifyListeners();

      const res = await fetch("/api/auth/user", {
        credentials: "include",
      });

      if (res.status === 401) {
        this.user = null;
        this.error = null;
      } else if (!res.ok) {
        this.error = new Error(`${res.status}: ${res.statusText}`);
        this.user = null;
      } else {
        this.user = await res.json();
        this.error = null;
      }
    } catch (err) {
      this.error = err;
      this.user = null;
    } finally {
      this.isLoading = false;
      this.hasInitialized = true;
      this.promise = null;
      this.saveCachedState();
      this.notifyListeners();
    }
  }

  subscribe(listener: () => void) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notifyListeners() {
    this.listeners.forEach(listener => listener());
  }

  getState() {
    return {
      user: this.user,
      isLoading: this.isLoading,
      error: this.error,
      isAuthenticated: !!this.user && !this.error,
    };
  }

  async initialize() {
    if (!this.hasInitialized && !this.promise) {
      await this.fetchUser();
    }
  }

  // Force refresh auth state (called after login)
  async refresh() {
    console.log('Forcing auth refresh');
    this.hasInitialized = false;
    this.promise = null;
    this.lastFetchTime = 0; // Force fresh fetch
    sessionStorage.removeItem(AUTH_STORAGE_KEY);
    sessionStorage.removeItem(AUTH_TIMESTAMP_KEY);
    await this.fetchUser();
  }
}

const authManager = AuthManager.getInstance();

export function useAuth() {
  const [state, setState] = useState(authManager.getState());

  useEffect(() => {
    // Initialize auth on first use
    authManager.initialize();

    // Only check for auth success parameter once
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('auth') === 'success') {
      // Force refresh auth state after login
      authManager.refresh();
      // Clean up URL immediately
      window.history.replaceState({}, '', window.location.pathname);
    }

    // Subscribe to changes
    const unsubscribe = authManager.subscribe(() => {
      setState(authManager.getState());
    });

    return unsubscribe;
  }, []); // Empty dependency array to run only once

  return state;
}