import React, { createContext, ReactNode } from 'react';
import { AuthContextType, AuthState, LoginCredentials, RegisterData, User, UserRole } from '../../types/auth';

// Create initial auth state
const initialAuthState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

// Create context
const MockAuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component
export const MockAuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Mock auth functions
  const login = async (credentials: LoginCredentials) => {
    console.log('Mock login called with:', credentials);
    throw new Error('Mock login not implemented');
  };

  const register = async (userData: RegisterData) => {
    console.log('Mock register called with:', userData);
    throw new Error('Mock register not implemented');
  };

  const logout = () => {
    console.log('Mock logout called');
  };

  const updateProfile = async (userData: Partial<User>) => {
    console.log('Mock updateProfile called with:', userData);
    throw new Error('Mock updateProfile not implemented');
  };

  const changePassword = async (currentPassword: string, newPassword: string) => {
    console.log('Mock changePassword called with:', currentPassword, newPassword);
    throw new Error('Mock changePassword not implemented');
  };

  const hasRole = (role: UserRole): boolean => {
    return false;
  };

  // Context value
  const contextValue: AuthContextType = {
    authState: initialAuthState,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    hasRole,
  };

  return (
    <MockAuthContext.Provider value={contextValue}>
      {children}
    </MockAuthContext.Provider>
  );
};

export default MockAuthContext;
