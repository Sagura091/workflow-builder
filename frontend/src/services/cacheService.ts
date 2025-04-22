import axios from 'axios';
import { API_BASE_URL } from '../config';

// Create axios instance for cache requests
const cacheApi = axios.create({
  baseURL: `${API_BASE_URL}/cache`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add interceptor to include auth token in requests
cacheApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Get cache statistics
 */
export const getCacheStats = async (): Promise<any> => {
  try {
    const response = await cacheApi.get('/stats');
    return response.data.data;
  } catch (error) {
    console.error('Error getting cache stats:', error);
    throw error;
  }
};

/**
 * Configure the cache
 */
export const configureCache = async (config: {
  max_size?: number;
  default_ttl?: number;
  cacheable_node_types?: string[];
}): Promise<void> => {
  try {
    await cacheApi.post('/configure', config);
  } catch (error) {
    console.error('Error configuring cache:', error);
    throw error;
  }
};

/**
 * Clear the cache
 */
export const clearCache = async (): Promise<void> => {
  try {
    await cacheApi.post('/clear');
  } catch (error) {
    console.error('Error clearing cache:', error);
    throw error;
  }
};

/**
 * Clean up expired cache entries
 */
export const cleanupCache = async (): Promise<{ removed_count: number }> => {
  try {
    const response = await cacheApi.post('/cleanup');
    return response.data.data;
  } catch (error) {
    console.error('Error cleaning up cache:', error);
    throw error;
  }
};

/**
 * Get cacheable node types
 */
export const getCacheableNodeTypes = async (): Promise<string[]> => {
  try {
    const response = await cacheApi.get('/cacheable-node-types');
    return response.data.data.cacheable_node_types;
  } catch (error) {
    console.error('Error getting cacheable node types:', error);
    throw error;
  }
};

/**
 * Set cacheable node types
 */
export const setCacheableNodeTypes = async (nodeTypes: string[]): Promise<void> => {
  try {
    await cacheApi.post('/cacheable-node-types', nodeTypes);
  } catch (error) {
    console.error('Error setting cacheable node types:', error);
    throw error;
  }
};

export default {
  getCacheStats,
  configureCache,
  clearCache,
  cleanupCache,
  getCacheableNodeTypes,
  setCacheableNodeTypes,
};
