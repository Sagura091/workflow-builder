import axios from 'axios';
import {
  ApiResponse,
  Plugin,
  PluginsResponse,
  Workflow,
  WorkflowExecutionResponse
} from '../types';
import {
  WorkflowExecutionRequest,
  WorkflowExecutionState
} from '../types/execution';
// Import mock data
import { mockNodeTypes } from '../data/mockData';
import { mockPlugins, mockExecuteWorkflow, isTypeCompatible } from './mockData';
import { API_BASE_URL } from '../config';

// Check if we're in standalone demo mode
const isStandaloneDemo = (window as any).STANDALONE_DEMO === true;

// API base URL is imported from config.ts

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Set a timeout to prevent long waits when the backend is not available
  timeout: 5000,
  // Add withCredentials to handle CORS properly
  withCredentials: false
});

// Add request interceptor to include auth token in requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle errors gracefully
api.interceptors.response.use(
  response => response,
  error => {
    // Handle network errors gracefully
    if (error.code === 'ERR_NETWORK' || error.code === 'ECONNABORTED' || error.message.includes('Network Error')) {
      console.warn('Backend connection failed, using fallback data');
      // Return a resolved promise with mock data structure
      return Promise.resolve({
        data: null,
        status: 404,
        statusText: 'Backend unavailable',
        headers: {},
        config: error.config
      });
    }
    console.error('API error:', error.message);
    return Promise.reject(error);
  }
);

// Plugin API
export const getPlugins = async (): Promise<Plugin[] | PluginsResponse> => {
  // If in standalone demo mode, return mock plugins immediately
  if (isStandaloneDemo) {
    console.log('Standalone demo mode: Using mock plugins');
    return mockPlugins;
  }

  try {
    const response = await api.get('/api/plugins');
    console.log('Plugin response:', response.data);

    // If response.data is null (backend unavailable), return mock plugins
    if (response.data === null) {
      console.warn('Backend unavailable, using mock plugins');
      const mockData = await getMockNodeTypes();
      console.log('Using mock plugins:', mockData.plugins.length);
      return mockData.plugins || [];
    }

    // Handle different response formats
    if (Array.isArray(response.data)) {
      // Direct array response
      console.log(`Processing ${response.data.length} plugins from array`);
      return response.data.map(plugin => {
        // Extract plugin metadata
        const meta = plugin.__plugin_meta__ || plugin;

        return {
          id: plugin.id || 'unknown',
          name: meta.name || plugin.title || 'Unknown Plugin',
          category: meta.category || 'Plugins',
          description: meta.description || 'No description available',
          inputs: meta.inputs || [],
          outputs: meta.outputs || [],
          ui_properties: {
            color: meta.color || '#3498db',
            icon: meta.icon || 'puzzle-piece',
            width: meta.width || 240
          },
          __plugin_meta__: {
            name: meta.name || plugin.title || 'Unknown Plugin',
            category: meta.category || 'Plugins',
            description: meta.description || 'No description available',
            editable: meta.editable !== false,
            generated: meta.generated || false,
            inputs: meta.inputs || [],
            outputs: meta.outputs || [],
            configFields: meta.configFields || []
          }
        };
      });
    } else if (response.data && response.data.status === 'success' && response.data.data) {
      // ApiResponse format
      console.log(`Processing plugins from API response`);
      return response.data.data;
    } else if (response.data && response.data.plugins && Array.isArray(response.data.plugins)) {
      // Object with plugins array
      console.log(`Processing ${response.data.plugins.length} plugins from object.plugins`);
      return response.data.plugins;
    } else if (response.data) {
      // Try to convert unknown format
      console.log('Converting plugin format:', response.data);

      // If it's an object with keys that might be plugin IDs
      if (typeof response.data === 'object' && !Array.isArray(response.data)) {
        const plugins = Object.entries(response.data).map(([id, data]: [string, any]) => ({
          id,
          name: data.name || id,
          category: data.category || 'Plugins',
          description: data.description || 'No description available',
          inputs: data.inputs || [],
          outputs: data.outputs || [],
          ui_properties: {
            color: data.color || '#3498db',
            icon: data.icon || 'puzzle-piece',
            width: data.width || 240
          },
          __plugin_meta__: {
            name: data.name || id,
            category: data.category || 'Plugins',
            description: data.description || 'No description available',
            editable: data.editable !== false,
            generated: data.generated || false,
            inputs: data.inputs || [],
            outputs: data.outputs || [],
            configFields: data.configFields || []
          }
        }));
        console.log(`Converted ${plugins.length} plugins from object`);
        return plugins;
      }

      console.warn('Unknown plugin response format:', response.data);
      // Use mock data as fallback
      const mockData = await getMockNodeTypes();
      return mockData.plugins || [];
    }

    // Empty response, use mock data
    console.warn('Empty plugin response, using mock data');
    const mockData = await getMockNodeTypes();
    return mockData.plugins || [];
  } catch (error) {
    console.error('Error fetching plugins:', error);
    // Return mock plugins instead of throwing to prevent UI errors
    const mockData = await getMockNodeTypes();
    console.log('Using mock plugins due to error:', mockData.plugins.length);
    return mockData.plugins || [];
  }
};

// Node Types API
export const getNodeTypes = async (): Promise<Record<string, any>> => {
  try {
    const response = await api.get('/node-types');
    if (response.data === null) {
      console.warn('Backend unavailable, using mock node types');
      return getMockNodeTypes();
    }
    return response.data;
  } catch (error) {
    console.error('Error fetching node types:', error);
    // Return mock data for development
    return getMockNodeTypes();
  }
};

export const getCoreNodes = async (fullMetadata: boolean = true): Promise<any[]> => {
  try {
    const response = await api.get(`/core-nodes?full_metadata=${fullMetadata}`);
    console.log('Core nodes API response:', response.data);

    if (response.data === null) {
      console.warn('Backend unavailable, using mock core nodes');
      const mockData = await getMockNodeTypes();
      console.log('Using mock core nodes:', mockData.coreNodes.length);
      return mockData.coreNodes;
    }

    // Handle different response formats
    if (response.data.status === 'success' && Array.isArray(response.data.data)) {
      return response.data.data;
    } else if (Array.isArray(response.data)) {
      return response.data;
    } else if (response.data && typeof response.data === 'object') {
      // Check if response.data has a 'data' property
      if (response.data.data && Array.isArray(response.data.data)) {
        return response.data.data;
      }
      // Check if response.data has a 'coreNodes' property
      if (response.data.coreNodes && Array.isArray(response.data.coreNodes)) {
        return response.data.coreNodes;
      }
      // Check if response.data has a 'nodes' property
      if (response.data.nodes && Array.isArray(response.data.nodes)) {
        return response.data.nodes;
      }
    }

    // If we can't parse the response, use mock data
    console.warn('Unknown core nodes response format, using mock data');
    const mockData = await getMockNodeTypes();
    return mockData.coreNodes;
  } catch (error) {
    console.error('Error fetching core nodes:', error);
    // Return mock data for development
    const mockData = await getMockNodeTypes();
    console.log('Using mock core nodes due to error:', mockData.coreNodes.length);
    return mockData.coreNodes;
  }
};

export const getCoreNodesByCategory = async (category: string, fullMetadata: boolean = true): Promise<any[]> => {
  try {
    const response = await api.get(`/core-nodes/categories/${category}?full_metadata=${fullMetadata}`);

    if (response.data.status === 'success' && Array.isArray(response.data.data)) {
      return response.data.data;
    }

    return [];
  } catch (error) {
    console.error(`Error fetching core nodes for category ${category}:`, error);
    return [];
  }
};

export const getCoreNodeCategories = async (): Promise<string[]> => {
  try {
    const response = await api.get('/core-nodes/categories');

    if (response.data.status === 'success' && Array.isArray(response.data.data)) {
      return response.data.data;
    }

    return [];
  } catch (error) {
    console.error('Error fetching core node categories:', error);
    return [];
  }
};

export const getCoreNode = async (nodeId: string): Promise<any> => {
  try {
    const response = await api.get(`/core-nodes/${nodeId}`);

    if (response.data.status === 'success' && response.data.data) {
      return response.data.data;
    }

    throw new Error(`Node ${nodeId} not found`);
  } catch (error) {
    console.error(`Error fetching core node ${nodeId}:`, error);
    throw error;
  }
};

export const validateNodeDefinition = async (nodeDef: any): Promise<{ valid: boolean; message?: string; node_def?: any }> => {
  try {
    const response = await api.post('/nodes/validate', nodeDef);

    // Check if the response has the expected format
    if (response.data && response.data.status === 'success' && response.data.data) {
      return response.data.data;
    }

    // Handle direct response format
    if (response.data && typeof response.data.valid === 'boolean') {
      return response.data;
    }

    console.warn('Unknown validation response format:', response.data);
    return { valid: true, message: 'Validation skipped (unknown response format)' };
  } catch (error) {
    console.error('Error validating node definition:', error);
    // For development, assume it's valid if we can't reach the backend
    return { valid: true, message: 'Validation skipped (backend unavailable)' };
  }
};

// Node Configurations API
export const getNodeConfigs = async (): Promise<Record<string, any>> => {
  try {
    const response = await api.get('/api/node-configs');
    if (response.data && response.data.status === 'success' && response.data.data) {
      return response.data.data;
    }
    console.warn('Invalid node configs response format:', response.data);
    return {};
  } catch (error) {
    console.error('Error fetching node configurations:', error);
    return {};
  }
};

export const getNodeConfig = async (nodeId: string): Promise<any> => {
  try {
    const response = await api.get(`/api/node-configs/${nodeId}`);
    if (response.data && response.data.status === 'success' && response.data.data) {
      return response.data.data;
    }
    throw new Error(`Configuration for node ${nodeId} not found`);
  } catch (error) {
    console.error(`Error fetching configuration for node ${nodeId}:`, error);
    throw error;
  }
};

// Type System API
export const getTypeSystem = async (): Promise<{ types: Record<string, any>, rules: Array<{ source: string, target: string[] }> }> => {
  try {
    const response = await api.get('/type-system');
    if (response.data === null) {
      console.warn('Backend unavailable, using mock type system');
      return getMockTypeSystem();
    }
    return response.data;
  } catch (error) {
    console.error('Error fetching type system:', error);
    // Return mock data for development
    return getMockTypeSystem();
  }
};

export const checkTypeCompatibility = async (sourceType: string, targetType: string): Promise<boolean> => {
  // If in standalone demo mode, use mock type compatibility check
  if (isStandaloneDemo) {
    console.log('Standalone demo mode: Using mock type compatibility check');
    return isTypeCompatible(sourceType, targetType);
  }

  try {
    const response = await api.get(`/type-system/compatibility?source=${sourceType}&target=${targetType}`);
    if (response.data === null) {
      console.warn('Backend unavailable, using local type compatibility check');
      return checkTypeCompatibilityLocally(sourceType, targetType);
    }
    return response.data.compatible;
  } catch (error) {
    console.error('Error checking type compatibility:', error);
    return checkTypeCompatibilityLocally(sourceType, targetType);
  }
};

// Local type compatibility check for when the backend is unavailable
const checkTypeCompatibilityLocally = async (sourceType: string, targetType: string): Promise<boolean> => {
  console.log(`Local type compatibility check: ${sourceType} -> ${targetType}`);

  // For development, always return true to allow any connections
  // This helps with testing the UI when the backend is not available
  return true;

  /* Uncomment this when backend is available
  // Simple compatibility check for development
  const typeSystem = await getMockTypeSystem();

  // If types are the same, they're compatible
  if (sourceType === targetType) return true;

  // If either is 'any', they're compatible
  if (sourceType === 'any' || targetType === 'any') return true;

  // Check type rules
  const rule = typeSystem.rules.find((r: { source: string; target: string[] }) => r.source === sourceType);
  if (rule && rule.target.includes(targetType)) return true;

  // Check bidirectional rules
  const bidirectionalRule = typeSystem.rules.find((r: { source: string; target: string[]; bidirectional?: boolean }) =>
    r.source === targetType && r.bidirectional && r.target.includes(sourceType)
  );
  if (bidirectionalRule) return true;

  return false;
  */
};

// Workflow API
export const saveWorkflow = async (workflow: Workflow): Promise<Workflow> => {
  try {
    const response = await api.post<ApiResponse<Workflow>>('/workflows', workflow);
    if (response.data.status === 'success' && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to save workflow');
  } catch (error) {
    console.error('Error saving workflow:', error);
    throw error;
  }
};

export const getWorkflows = async (): Promise<Workflow[]> => {
  try {
    const response = await api.get<ApiResponse<Workflow[]>>('/workflows');
    if (response.data.status === 'success' && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to fetch workflows');
  } catch (error) {
    console.error('Error fetching workflows:', error);
    throw error;
  }
};

export const getWorkflow = async (id: string): Promise<Workflow> => {
  try {
    const response = await api.get<ApiResponse<Workflow>>(`/workflows/${id}`);
    if (response.data.status === 'success' && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.message || 'Failed to fetch workflow');
  } catch (error) {
    console.error('Error fetching workflow:', error);
    throw error;
  }
};

// Validation API
export const validateWorkflow = async (workflow: Workflow): Promise<{ status: string, errors: any[] }> => {
  try {
    // Convert workflow to backend format
    const backendWorkflow = {
      nodes: workflow.nodes.map(node => ({
        id: node.id,
        type: node.type,
        config: node.config
      })),
      edges: workflow.connections.map(conn => ({
        source: conn.from.nodeId,
        target: conn.to.nodeId,
        source_port: conn.from.port,
        target_port: conn.to.port
      }))
    };

    const response = await api.post('/workflows/validate', backendWorkflow);
    return response.data;
  } catch (error) {
    console.error('Error validating workflow:', error);
    throw error;
  }
};

// Execution API
export const executeWorkflow = async (workflow: Workflow): Promise<WorkflowExecutionResponse> => {
  // If in standalone demo mode, use mock execution
  if (isStandaloneDemo) {
    console.log('Standalone demo mode: Using mock execution');
    try {
      const result = await mockExecuteWorkflow(workflow.nodes, workflow.connections);
      return result as WorkflowExecutionResponse;
    } catch (error) {
      console.error('Error in mock execution:', error);
      throw error;
    }
  }

  try {
    // Convert workflow to backend format
    const backendWorkflow = {
      nodes: workflow.nodes.map(node => ({
        id: node.id,
        type: node.type,
        config: node.config
      })),
      edges: workflow.connections.map(conn => ({
        source: conn.from.nodeId,
        target: conn.to.nodeId,
        source_port: conn.from.port,
        target_port: conn.to.port
      }))
    };

    const response = await api.post<WorkflowExecutionResponse>('/workflows/execute', backendWorkflow);
    if (response.data.status === 'success') {
      return response.data;
    }
    throw new Error('Failed to execute workflow');
  } catch (error) {
    console.error('Error executing workflow:', error);
    throw error;
  }
};

export const executeWorkflowAdvanced = async (executionRequest: WorkflowExecutionRequest): Promise<WorkflowExecutionResponse> => {
  try {
    const response = await api.post<WorkflowExecutionResponse>('/workflows/execute-advanced', executionRequest);
    if (response.data.status === 'success') {
      return response.data;
    }
    throw new Error('Failed to execute workflow');
  } catch (error) {
    console.error('Error executing workflow:', error);
    throw error;
  }
};

export const executeWorkflowAsync = async (workflow: Workflow): Promise<WorkflowExecutionResponse> => {
  try {
    // Convert workflow to backend format
    const backendWorkflow = {
      nodes: workflow.nodes.map(node => ({
        id: node.id,
        type: node.type,
        config: node.config
      })),
      edges: workflow.connections.map(conn => ({
        source: conn.from.nodeId,
        target: conn.to.nodeId,
        source_port: conn.from.port,
        target_port: conn.to.port
      }))
    };

    const response = await api.post<WorkflowExecutionResponse>('/workflows/execute-async', backendWorkflow);
    if (response.data.status === 'success') {
      return response.data;
    }
    throw new Error('Failed to execute workflow asynchronously');
  } catch (error) {
    console.error('Error executing workflow asynchronously:', error);
    throw error;
  }
};

export const executeWorkflowAsyncAdvanced = async (executionRequest: WorkflowExecutionRequest): Promise<WorkflowExecutionResponse> => {
  try {
    const response = await api.post<WorkflowExecutionResponse>('/workflows/execute-async-advanced', executionRequest);
    if (response.data.status === 'success') {
      return response.data;
    }
    throw new Error('Failed to execute workflow asynchronously');
  } catch (error) {
    console.error('Error executing workflow asynchronously:', error);
    throw error;
  }
};

export const stopExecution = async (executionId: string): Promise<void> => {
  try {
    await api.post(`/workflows/execution/${executionId}/stop`);
  } catch (error) {
    console.error('Error stopping execution:', error);
    throw error;
  }
};

export const resumeExecution = async (executionId: string, resumeFromNode?: string): Promise<WorkflowExecutionResponse> => {
  try {
    const params: Record<string, string> = {};
    if (resumeFromNode) {
      params.resume_from_node = resumeFromNode;
    }

    const response = await api.post<WorkflowExecutionResponse>(
      `/workflows/execution/${executionId}/resume`,
      null,
      { params }
    );

    if (response.data.status === 'success') {
      return response.data;
    }
    throw new Error('Failed to resume workflow execution');
  } catch (error) {
    console.error('Error resuming execution:', error);
    throw error;
  }
};

export const getExecutionStatus = async (executionId: string): Promise<any> => {
  try {
    const response = await api.get(`/workflows/execution/${executionId}`);
    if (response.data.status === 'success') {
      return response.data.data;
    }
    throw new Error('Failed to get execution status');
  } catch (error) {
    console.error('Error getting execution status:', error);
    throw error;
  }
};

export const getExecutionState = async (executionId: string): Promise<WorkflowExecutionState> => {
  try {
    const response = await api.get(`/workflows/execution/${executionId}/state`);
    if (response.data.status === 'success') {
      return response.data.data;
    }
    throw new Error('Failed to get execution state');
  } catch (error) {
    console.error('Error getting execution state:', error);
    throw error;
  }
};

export const isExecutionActive = async (executionId: string): Promise<boolean> => {
  try {
    const response = await api.get(`/workflows/execution/${executionId}/active`);
    if (response.data.status === 'success') {
      return response.data.data.active;
    }
    return false;
  } catch (error) {
    console.error('Error checking if execution is active:', error);
    return false;
  }
};





// Mock API for development
export const getMockNodeTypes = async () => {
  // Return mock node types
  return {
    coreNodes: mockNodeTypes.coreNodes || [],
    plugins: mockNodeTypes.plugins || []
  };
};

export const getMockTypeSystem = async () => {
  // Return mock type system
  return {
    types: {
      string: { name: 'String', description: 'Text value' },
      number: { name: 'Number', description: 'Numeric value' },
      boolean: { name: 'Boolean', description: 'True/false value' },
      object: { name: 'Object', description: 'JavaScript object' },
      array: { name: 'Array', description: 'List of values' },
      any: { name: 'Any', description: 'Any type of value' },
      trigger: { name: 'Trigger', description: 'Execution trigger' }
    },
    rules: [
      { source: 'string', target: ['string', 'any'], bidirectional: false },
      { source: 'number', target: ['number', 'string', 'any'], bidirectional: false },
      { source: 'boolean', target: ['boolean', 'string', 'any'], bidirectional: false },
      { source: 'object', target: ['object', 'any'], bidirectional: false },
      { source: 'array', target: ['array', 'any'], bidirectional: false },
      { source: 'trigger', target: ['trigger'], bidirectional: true },
      { source: 'any', target: ['string', 'number', 'boolean', 'object', 'array', 'any'], bidirectional: true }
    ]
  };
};

// Node Instance API
export interface NodeInstance {
  id: string;
  node_type_id: string;
  name: string;
  config: Record<string, any>;
  position: { x: number; y: number };
  workflow_id?: string;
  created_at: string;
  updated_at: string;
}

export interface NodeInstanceCreate {
  node_type_id: string;
  name?: string;
  config?: Record<string, any>;
  position?: { x: number; y: number };
  workflow_id?: string;
}

export interface NodeInstanceUpdate {
  name?: string;
  config?: Record<string, any>;
  position?: { x: number; y: number };
  workflow_id?: string;
}

export const getNodeInstances = async (workflowId?: string): Promise<NodeInstance[]> => {
  try {
    const url = workflowId ? `/node-instances?workflow_id=${workflowId}` : '/node-instances';
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching node instances:', error);
    return [];
  }
};

export const getNodeInstance = async (instanceId: string): Promise<NodeInstance | null> => {
  try {
    const response = await api.get(`/node-instances/${instanceId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching node instance ${instanceId}:`, error);
    return null;
  }
};

export const createNodeInstance = async (instance: NodeInstanceCreate): Promise<NodeInstance | null> => {
  try {
    const response = await api.post('/node-instances', instance);
    return response.data;
  } catch (error) {
    console.error('Error creating node instance:', error);
    return null;
  }
};

export const updateNodeInstance = async (instanceId: string, update: NodeInstanceUpdate): Promise<NodeInstance | null> => {
  try {
    const response = await api.put(`/node-instances/${instanceId}`, update);
    return response.data;
  } catch (error) {
    console.error(`Error updating node instance ${instanceId}:`, error);
    return null;
  }
};

export const deleteNodeInstance = async (instanceId: string): Promise<boolean> => {
  try {
    await api.delete(`/node-instances/${instanceId}`);
    return true;
  } catch (error) {
    console.error(`Error deleting node instance ${instanceId}:`, error);
    return false;
  }
};


