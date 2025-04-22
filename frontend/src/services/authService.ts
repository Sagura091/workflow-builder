import axios from 'axios';
import { API_BASE_URL } from '../config';
import { User, LoginCredentials, RegisterData, UserRole } from '../types/auth';

// Create axios instance for auth requests
const authApi = axios.create({
  baseURL: `${API_BASE_URL}/auth`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add interceptor to include auth token in requests
authApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle token expiration
authApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If the error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await authApi.post('/token/refresh', { refresh_token: refreshToken });
          const { access_token } = response.data;
          
          // Update the token in localStorage
          localStorage.setItem('auth_token', access_token);
          
          // Update the Authorization header
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          
          // Retry the original request
          return axios(originalRequest);
        }
      } catch (refreshError) {
        // If refresh fails, log out the user
        logout();
      }
    }
    
    return Promise.reject(error);
  }
);

/**
 * Login user with credentials
 */
export const login = async (credentials: LoginCredentials): Promise<{ user: User; token: string }> => {
  try {
    const response = await authApi.post('/token', new URLSearchParams({
      username: credentials.username,
      password: credentials.password,
    }), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    const { access_token, token_type, expires_at, user } = response.data;
    
    // Store token in localStorage
    localStorage.setItem('auth_token', access_token);
    localStorage.setItem('token_expires', expires_at);
    
    return { user, token: access_token };
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

/**
 * Register a new user
 */
export const register = async (userData: RegisterData): Promise<User> => {
  try {
    const response = await authApi.post('/register', userData);
    return response.data;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
};

/**
 * Get current user profile
 */
export const getCurrentUser = async (): Promise<User> => {
  try {
    const response = await authApi.get('/me');
    return response.data;
  } catch (error) {
    console.error('Get current user error:', error);
    throw error;
  }
};

/**
 * Update user profile
 */
export const updateUserProfile = async (userData: Partial<User>): Promise<User> => {
  try {
    const response = await authApi.put('/me', userData);
    return response.data;
  } catch (error) {
    console.error('Update profile error:', error);
    throw error;
  }
};

/**
 * Change user password
 */
export const changePassword = async (currentPassword: string, newPassword: string): Promise<void> => {
  try {
    await authApi.post('/change-password', { current_password: currentPassword, new_password: newPassword });
  } catch (error) {
    console.error('Change password error:', error);
    throw error;
  }
};

/**
 * Logout user
 */
export const logout = (): void => {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('token_expires');
  
  // Redirect to login page
  window.location.href = '/login';
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  const token = localStorage.getItem('auth_token');
  const expires = localStorage.getItem('token_expires');
  
  if (!token || !expires) {
    return false;
  }
  
  // Check if token is expired
  const expiresDate = new Date(expires);
  if (expiresDate < new Date()) {
    // Token is expired, remove it
    localStorage.removeItem('auth_token');
    localStorage.removeItem('token_expires');
    return false;
  }
  
  return true;
};

/**
 * Check if user has a specific role
 */
export const hasRole = async (role: UserRole): Promise<boolean> => {
  try {
    const user = await getCurrentUser();
    return user.role === role;
  } catch (error) {
    return false;
  }
};

export default {
  login,
  register,
  getCurrentUser,
  updateUserProfile,
  changePassword,
  logout,
  isAuthenticated,
  hasRole,
};
