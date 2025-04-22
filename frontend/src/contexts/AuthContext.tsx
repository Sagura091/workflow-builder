import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import {
  AuthContextType,
  AuthState,
  LoginCredentials,
  RegisterData,
  User,
  UserRole
} from '../types/auth';
import * as authService from '../services/authService';

// Create initial auth state
const initialAuthState: AuthState = {
  user: null,
  token: localStorage.getItem('auth_token'),
  isAuthenticated: authService.isAuthenticated(),
  isLoading: true,
  error: null,
};

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>(initialAuthState);

  // Load user on mount
  useEffect(() => {
    const loadUser = async () => {
      if (authState.token) {
        try {
          const user = await authService.getCurrentUser();
          setAuthState(prev => ({
            ...prev,
            user,
            isAuthenticated: true,
            isLoading: false,
          }));
        } catch (error) {
          console.error('Failed to load user:', error);
          setAuthState(prev => ({
            ...prev,
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: 'Session expired. Please log in again.',
          }));
          // Clear localStorage
          localStorage.removeItem('auth_token');
          localStorage.removeItem('token_expires');
        }
      } else {
        setAuthState(prev => ({
          ...prev,
          isLoading: false,
        }));
      }
    };

    loadUser();
  }, [authState.token]);

  // Login function
  const login = async (credentials: LoginCredentials) => {
    setAuthState(prev => ({
      ...prev,
      isLoading: true,
      error: null,
    }));

    try {
      const { user, token } = await authService.login(credentials);

      setAuthState({
        user,
        token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error: any) {
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: error.response?.data?.message || 'Login failed. Please check your credentials.',
      }));
      throw error;
    }
  };

  // Register function
  const register = async (userData: RegisterData) => {
    setAuthState(prev => ({
      ...prev,
      isLoading: true,
      error: null,
    }));

    try {
      const user = await authService.register(userData);

      setAuthState(prev => ({
        ...prev,
        isLoading: false,
      }));

      // Return void to match interface
    } catch (error: any) {
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: error.response?.data?.message || 'Registration failed. Please try again.',
      }));
      throw error;
    }
  };

  // Logout function
  const logout = () => {
    // Clear localStorage
    localStorage.removeItem('auth_token');
    localStorage.removeItem('token_expires');

    // Reset state
    setAuthState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  };

  // Update profile function
  const updateProfile = async (userData: Partial<User>) => {
    setAuthState(prev => ({
      ...prev,
      isLoading: true,
      error: null,
    }));

    try {
      const updatedUser = await authService.updateUserProfile(userData);

      setAuthState(prev => ({
        ...prev,
        user: updatedUser,
        isLoading: false,
      }));
    } catch (error: any) {
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: error.response?.data?.message || 'Failed to update profile.',
      }));
      throw error;
    }
  };

  // Change password function
  const changePassword = async (currentPassword: string, newPassword: string) => {
    setAuthState(prev => ({
      ...prev,
      isLoading: true,
      error: null,
    }));

    try {
      await authService.changePassword(currentPassword, newPassword);

      setAuthState(prev => ({
        ...prev,
        isLoading: false,
      }));
    } catch (error: any) {
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: error.response?.data?.message || 'Failed to change password.',
      }));
      throw error;
    }
  };

  // Check if user has a specific role
  const hasRole = (role: UserRole): boolean => {
    return authState.user?.role === role;
  };

  // Context value
  const contextValue: AuthContextType = {
    authState,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    hasRole,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
