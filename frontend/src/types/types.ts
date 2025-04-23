// API Response type
export interface ApiResponse<T> {
  status: 'success' | 'error';
  message?: string;
  data?: T;
}

// Config field type for node configuration
export interface ConfigField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'textarea' | 'checkbox' | 'code' | 'json' | 'color';
  placeholder?: string;
  options?: string[];
  multiple?: boolean;
  min?: number;
  max?: number;
  step?: number;
  language?: 'javascript' | 'python' | 'json' | 'html' | 'css';
  height?: string;
  helpText?: string;
  [key: string]: any;
}

// Plugin types
export interface PluginMetadata {
  name: string;
  category: string;
  description: string;
  editable: boolean;
  generated: boolean;
  inputs: Record<string, any>;
  outputs: Record<string, any>;
  configFields: ConfigField[];
  [key: string]: any;
}

export interface Plugin {
  id: string;
  __plugin_meta__: PluginMetadata;
  [key: string]: any;
}

export interface PluginResponse {
  plugins?: Plugin[];
  [key: string]: any;
}

// Node types
export interface NodePort {
  id: string;
  name: string;
  type: string;
  description?: string;
  required?: boolean;
  ui_properties?: {
    position?: string;
    [key: string]: any;
  };
}

export interface NodeData {
  id: string;
  type: string;
  x: number;
  y: number;
  config: Record<string, any>;
  width?: number;
  height?: number;
  label?: string;
}

export interface NodeDefinition {
  id: string;
  name: string;
  category: string;
  description: string;
  inputs: NodePort[];
  outputs: NodePort[];
  ui_properties?: {
    color: string;
    icon: string;
    width?: number;
    [key: string]: any;
  };
}

// Connection types
export interface ConnectionEndpoint {
  nodeId: string;
  port: string;
}

export interface Connection {
  id: string;
  from: ConnectionEndpoint;
  to: ConnectionEndpoint;
}

// Workflow types
export interface Workflow {
  id: string | null;
  name: string;
  nodes: NodeData[];
  connections: Connection[];
  description?: string;
  created_at?: string;
  updated_at?: string;
}

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
  connectionStyle: 'straight' | 'bezier' | 'fluid';
  validationErrors: string[];
}

// Execution types
export interface WorkflowExecutionResponse {
  status: string;
  execution_id?: string;
  results?: Record<string, any>;
  errors?: string[];
  logs?: Array<{
    node: string;
    message: string;
    timestamp: string;
    level: 'info' | 'warning' | 'error';
  }>;
}

export interface NodeExecutionStatus {
  status: 'pending' | 'running' | 'completed' | 'failed';
  start_time?: string;
  end_time?: string;
  duration?: number;
  error?: string;
}

export interface ExecutionStatus {
  status: 'pending' | 'running' | 'completed' | 'failed';
  node_statuses: Record<string, NodeExecutionStatus>;
  start_time?: string;
  end_time?: string;
  duration?: number;
  logs?: Array<{
    node: string;
    message: string;
    timestamp: string;
    level: 'info' | 'warning' | 'error';
  }>;
}

export interface DataFlowEvent {
  sourceNodeId: string;
  targetNodeId: string;
  sourcePort: string;
  targetPort: string;
  value: any;
  timestamp: string;
}

// Type system types
export interface TypeDefinition {
  description: string;
  ui_properties: {
    color: string;
    icon: string;
    [key: string]: any;
  };
}

export interface TypeRule {
  source: string;
  target: string[];
  bidirectional?: boolean;
}

export interface TypeSystem {
  types: Record<string, TypeDefinition>;
  rules: TypeRule[];
}
