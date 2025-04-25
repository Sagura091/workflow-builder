// Node Types
export interface NodeConfig {
  title: string;
  icon: string;
  color: string;
  inputs: string[];
  outputs: string[];
  configFields: ConfigField[];
}

export interface ConfigField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'textarea' | 'checkbox' | 'code' | 'json' | 'color';
  placeholder?: string;
  options?: string[];
  multiple?: boolean;
  min?: number;
  step?: number;
  language?: 'javascript' | 'python' | 'json' | 'html' | 'css';
  height?: string;
  helpText?: string;
}

export interface NodeData {
  id: string;
  type: string;
  x: number;
  y: number;
  width?: number;
  height?: number;
  title?: string;
  config: Record<string, any>;
}

// Connection Types
export interface ConnectionPoint {
  nodeId: string;
  port: string;
  el?: HTMLElement;
}

export interface Connection {
  id: string;
  from: ConnectionPoint;
  to: ConnectionPoint;
  line?: any; // This will be the leader-line instance
}

// Plugin Types
export interface PluginMeta {
  name: string;
  category: string;
  description: string;
  editable: boolean;
  generated: boolean;
  inputs: Record<string, string>;
  outputs: Record<string, string>;
  configFields: ConfigField[];
}

export interface Plugin {
  id: string;
  name?: string;
  category?: string;
  description?: string;
  inputs?: any[];
  outputs?: any[];
  ui_properties?: Record<string, any>;
  __plugin_meta__?: PluginMeta;
}

// Workflow Types
export interface Workflow {
  id: string | null;
  name: string;
  nodes: NodeData[];
  connections: Connection[];
  lastSaved?: string;
  description?: string;
  created?: string;
  modified?: string;
  exported?: string;
}

// State Types
export interface WorkflowState {
  nodes: NodeData[];
  connections: Connection[];
  currentNodeId: number;
  selectedNode: string | null;
  selectedConnection: string | null;
  draggedNode: string | null;
  isExecuting: boolean;
  lines: any[];
  currentWorkflow: Workflow;
  tempConnection: {
    fromNodeId: string;
    fromPort: string;
    fromEl: HTMLElement;
  } | null;
  zoom: {
    level: number;
    min: number;
    max: number;
    step: number;
  };
  history: {
    past: WorkflowState[];
    future: WorkflowState[];
  };
  connectionStyle: 'fluid' | 'straight' | 'grid';
  validationErrors: ValidationError[];
}

// Validation Types
export interface ValidationError {
  type: 'node' | 'connection';
  id: string;
  message: string;
}

// Execution Types
// Re-export all execution types from the dedicated file
export * from './execution';

// API Response Types
export interface ApiResponse<T> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
}

export interface PluginsResponse {
  status: 'success';
  plugins: Plugin[];
}

export interface WorkflowExecutionResponse {
  status: 'success';
  executionId: string;
  results?: {
    node_outputs: Record<string, any>;
    log: any[];
  };
}
