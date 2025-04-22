/**
 * Schedule Types
 */

export enum ScheduleType {
  CRON = 'cron',
  INTERVAL = 'interval',
  ONE_TIME = 'one_time',
  EVENT = 'event'
}

export enum ScheduleStatus {
  ACTIVE = 'active',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export interface ScheduleRequest {
  workflow_id: string;
  name: string;
  description?: string;
  schedule_type: ScheduleType;
  cron_expression?: string;
  interval_seconds?: number;
  start_time?: string;
  end_time?: string;
  max_executions?: number;
  execution_options?: Record<string, any>;
  tags?: string[];
}

export interface Schedule {
  id: string;
  workflow_id: string;
  name: string;
  description?: string;
  schedule_type: ScheduleType;
  cron_expression?: string;
  interval_seconds?: number;
  start_time?: string;
  end_time?: string;
  next_execution_time?: string;
  last_execution_time?: string;
  last_execution_id?: string;
  last_execution_status?: string;
  execution_count: number;
  max_executions?: number;
  execution_options?: Record<string, any>;
  status: ScheduleStatus;
  created_at: string;
  updated_at: string;
  tags?: string[];
}

export interface ScheduleExecutionLog {
  id: string;
  schedule_id: string;
  workflow_id: string;
  execution_id: string;
  status: string;
  start_time: string;
  end_time?: string;
  duration_seconds?: number;
  error_message?: string;
}
