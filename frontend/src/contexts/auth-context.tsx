"use client"

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import toast from 'react-hot-toast';
import { login, register, logout, getCurrentUser, refreshToken, type User, type LoginRequest, type RegisterRequest } from '@/lib/auth';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  isAdmin: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'auth_token';
const TOKEN_EXPIRY_KEY = 'token_expiry';
const USER_KEY = 'user_data';

// Token expiry time in milliseconds (30 minutes)
const TOKEN_EXPIRY_MS = 30 * 60 * 1000;

// Warning before expiry (5 minutes)
const TOKEN_WARNING_MS = 5 * 60 * 1000;

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const pathname = usePathname();

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = () => {
      try {
        const storedToken = localStorage.getItem(TOKEN_KEY);
        const storedExpiry = localStorage.getItem(TOKEN_EXPIRY_KEY);
        const storedUser = localStorage.getItem(USER_KEY);

        if (storedToken && storedExpiry && storedUser) {
          const expiry = parseInt(storedExpiry, 10);
          const now = Date.now();

          if (now < expiry) {
            // Token is still valid
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
          } else {
            // Token expired
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem(TOKEN_EXPIRY_KEY);
            localStorage.removeItem(USER_KEY);
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(TOKEN_EXPIRY_KEY);
        localStorage.removeItem(USER_KEY);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  // Token expiry checker with auto-redirect
  useEffect(() => {
    if (!token) return;

    const checkTokenExpiry = () => {
      const storedExpiry = localStorage.getItem(TOKEN_EXPIRY_KEY);
      if (!storedExpiry) return;

      const expiry = parseInt(storedExpiry, 10);
      const now = Date.now();
      const timeLeft = expiry - now;

      if (timeLeft <= 0) {
        // Token already expired
        console.log('Token expired, redirecting to login...');
        handleLogout(true);
      } else if (timeLeft <= TOKEN_WARNING_MS) {
        // Show warning (optional - can add toast notification)
        console.log(`Token expiring in ${Math.floor(timeLeft / 1000 / 60)} minutes`);
        // Optionally refresh token automatically
        handleRefreshToken();
      }
    };

    // Check every minute
    const interval = setInterval(checkTokenExpiry, 60000);
    return () => clearInterval(interval);
  }, [token]);

  // Auto-redirect unauthenticated users from protected routes
  useEffect(() => {
    const protectedRoutes = ['/dashboard', '/dashboard/'];
    const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route));

    if (!isLoading && !user && isProtectedRoute) {
      console.log('Unauthenticated user trying to access protected route, redirecting to login...');
      router.push('/login?redirect=' + encodeURIComponent(pathname));
    }
    
    // Redirect authenticated users away from login/signup pages
    const authPages = ['/login', '/signup'];
    const isAuthPage = authPages.some(page => pathname === page || pathname.startsWith(page + '/'));
    
    if (!isLoading && user && isAuthPage) {
      console.log('Authenticated user on auth page, redirecting to dashboard...');
      router.push('/dashboard');
    }
  }, [user, isLoading, pathname, router]);

  const handleLogin = async (data: LoginRequest) => {
    try {
      setError(null);
      const response = await login(data);

      const now = Date.now();
      const expiry = now + TOKEN_EXPIRY_MS;

      setToken(response.access_token);
      setUser(response.user);

      localStorage.setItem(TOKEN_KEY, response.access_token);
      localStorage.setItem(TOKEN_EXPIRY_KEY, expiry.toString());
      localStorage.setItem(USER_KEY, JSON.stringify(response.user));

      // Show success toast
      toast.success(`Welcome back, ${response.user.name}!`, {
        icon: '👋',
      });

      // Redirect to dashboard or the page user was trying to access
      const params = new URLSearchParams(window.location.search);
      const redirect = params.get('redirect') || '/dashboard';
      router.push(redirect);
    } catch (err: any) {
      setError(err.message || 'Login failed');
      toast.error(err.message || 'Invalid email or password', {
        icon: '❌',
      });
      throw err;
    }
  };

  const handleRegister = async (data: RegisterRequest) => {
    try {
      setError(null);
      const response = await register(data);

      // Show success toast
      toast.success(`Account created successfully, ${response.user.name}!`, {
        icon: '🎉',
        duration: 5000,
      });

      // Redirect to login page
      setTimeout(() => {
        router.push('/login?registered=true');
      }, 1000);
    } catch (err: any) {
      setError(err.message || 'Registration failed');
      toast.error(err.message || 'Registration failed. Please try again.', {
        icon: '❌',
      });
      throw err;
    }
  };

  const handleLogout = useCallback((expired = false) => {
    // Clear token from state
    setToken(null);
    setUser(null);
    
    // Clear localStorage
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(TOKEN_EXPIRY_KEY);
    localStorage.removeItem(USER_KEY);

    if (expired) {
      toast.error('Session expired. Please login again.', {
        icon: '⏰',
      });
      router.push('/login?expired=true');
    } else {
      toast.success('Logged out successfully', {
        icon: '👋',
      });
      router.push('/login');
    }
  }, [router]);

  const handleRefreshToken = async () => {
    if (!token) return;

    try {
      const response = await refreshToken(token);
      const now = Date.now();
      const expiry = now + TOKEN_EXPIRY_MS;

      setToken(response.access_token);
      localStorage.setItem(TOKEN_KEY, response.access_token);
      localStorage.setItem(TOKEN_EXPIRY_KEY, expiry.toString());
      console.log('Token refreshed successfully');
    } catch (error) {
      console.error('Token refresh failed:', error);
      handleLogout(true);
    }
  };

  const value = {
    user,
    token,
    isLoading,
    isAuthenticated: !!user && !!token,
    isAdmin: user?.role === 'admin',
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    error,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
