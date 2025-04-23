/**
 * Configuration
 *
 * This file contains configuration values for the application.
 */

// API configuration
export const API_BASE_URL = 'http://localhost:8001';
export const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8001/ws';

// WebSocket configuration
export const WS_RECONNECT_INTERVAL = 2000; // 2 seconds
export const WS_MAX_RECONNECT_ATTEMPTS = 5;

// UI configuration
export const DEFAULT_NODE_WIDTH = 200;
export const DEFAULT_NODE_HEIGHT = 100;
export const NODE_HANDLE_SIZE = 10;
export const GRID_SIZE = 20;
export const SNAP_TO_GRID = true;

// Type system configuration
export const TYPE_COLORS = {
  string: '#60a5fa',
  number: '#a78bfa',
  boolean: '#f87171',
  object: '#4ade80',
  array: '#fbbf24',
  any: '#9ca3af',
  trigger: '#ec4899',
  dataset: '#0ea5e9',
  model: '#8b5cf6',
  features: '#10b981',
  predictions: '#f59e0b',
  metrics: '#fb923c',
  service: '#a855f7',
  labels: '#fbbf24'
};

// Default values
export const DEFAULT_WORKFLOW_NAME = 'New Workflow';
export const DEFAULT_WORKFLOW_DESCRIPTION = 'A new workflow created with Workflow Builder';

// Authentication settings
export const AUTH_TOKEN_KEY = 'auth_token';
export const AUTH_TOKEN_EXPIRES_KEY = 'token_expires';

// Feature flags
export const FEATURES = {
  WEBSOCKETS_ENABLED: true,
  NODE_INSTANCES_ENABLED: true,
  LAZY_LOADING_ENABLED: true,
  ENABLE_TEMPLATES: true,
  ENABLE_SCHEDULING: true,
  ENABLE_CACHING: true,
  ENABLE_PARTIAL_EXECUTION: true,
  ENABLE_TYPE_VALIDATION: true,
  ENABLE_DARK_MODE: true,
};

// Version information
export const APP_VERSION = process.env.REACT_APP_VERSION || '1.0.0';

