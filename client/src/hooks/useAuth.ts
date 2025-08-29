import { useState, useEffect } from "react";

// Singleton auth state to prevent multiple requests
class AuthManager {
  private static instance: AuthManager;
  private user: any = null;
  private isLoading = true;
  private error: any = null;
  private hasInitialized = false;
  private listeners: Array<() => void> = [];
  private promise: Promise<any> | null = null;

  static getInstance() {
    if (!AuthManager.instance) {
      AuthManager.instance = new AuthManager();
    }
    return AuthManager.instance;
  }

  async fetchUser() {
    if (this.promise) {
      return this.promise; // Return existing promise if already fetching
    }

    this.promise = this.doFetch();
    return this.promise;
  }

  private async doFetch() {
    try {
      this.isLoading = true;
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
}

const authManager = AuthManager.getInstance();

export function useAuth() {
  const [state, setState] = useState(authManager.getState());

  useEffect(() => {
    // Initialize auth on first use
    authManager.initialize();

    // Subscribe to changes
    const unsubscribe = authManager.subscribe(() => {
      setState(authManager.getState());
    });

    return unsubscribe;
  }, []);

  return state;
}