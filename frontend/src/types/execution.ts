/**
 * Execution Types
 */

export enum ExecutionMode {
  FULL = 'full',
  PARTIAL = 'partial',
  RESUME = 'resume'
}

export enum ExecutionStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  STOPPED = 'stopped',
  PAUSED = 'paused'
}

export enum NodeExecutionStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  SKIPPED = 'skipped',
  CACHED = 'cached'
}

export interface NodeExecutionResult {
  node_id: string;
  node_type: string;
  status: NodeExecutionStatus;
  outputs: Record<string, any>;
  execution_time_ms?: number;
  start_time?: string;
  end_time?: string;
  error?: string;
  cached: boolean;
}

export interface ExecutionLog {
  node: string;
  status: string;
  value: any;
  timestamp: string;
  execution_time_ms?: number;
  cached?: boolean;
  traceback?: string;
}

export interface ExecutionResult {
  execution_id: string;
  status: ExecutionStatus;
  node_outputs: Record<string, any>;
  node_results: Record<string, NodeExecutionResult>;
  log: ExecutionLog[];
  start_time?: string;
  end_time?: string;
  execution_time_ms?: number;
  error?: string;
  traceback?: string;
}

export interface WorkflowExecutionState {
  execution_id: string;
  workflow_id: string;
  status: ExecutionStatus;
  node_statuses: Record<string, NodeExecutionStatus>;
  current_node?: string;
  completed_nodes: string[];
  failed_nodes: string[];
  skipped_nodes: string[];
  start_time: string;
  end_time?: string;
  execution_time_ms?: number;
  execution_mode: ExecutionMode;
  selected_nodes: string[];
  resume_from_node?: string;
  previous_execution_id?: string;
}

export interface WorkflowExecutionRequest {
  workflow: {
    id?: string;
    name?: string;
    nodes: any[];
    edges: any[];
  };
  execution_mode: ExecutionMode;
  selected_nodes?: string[];
  resume_from_node?: string;
  previous_execution_id?: string;
  execution_options?: Record<string, any>;
}

export interface WorkflowExecutionResponse {
  status: string;
  execution_id: string;
  results?: ExecutionResult;
  message?: string;
  error?: string;
}
