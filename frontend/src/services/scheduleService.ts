import axios from 'axios';
import { API_BASE_URL } from '../config';
import { Schedule, ScheduleRequest, ScheduleExecutionLog, ScheduleStatus } from '../types/schedule';

// Create axios instance for schedule requests
const scheduleApi = axios.create({
  baseURL: `${API_BASE_URL}/schedules`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add interceptor to include auth token in requests
scheduleApi.interceptors.request.use(
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
 * Create a new schedule
 */
export const createSchedule = async (scheduleData: ScheduleRequest): Promise<Schedule> => {
  try {
    const response = await scheduleApi.post('', scheduleData);
    return response.data.data;
  } catch (error) {
    console.error('Error creating schedule:', error);
    throw error;
  }
};

/**
 * Get all schedules with optional filtering
 */
export const getSchedules = async (
  workflowId?: string,
  status?: ScheduleStatus,
  tag?: string
): Promise<Schedule[]> => {
  try {
    const params: Record<string, string> = {};
    
    if (workflowId) {
      params.workflow_id = workflowId;
    }
    
    if (status) {
      params.status = status;
    }
    
    if (tag) {
      params.tag = tag;
    }
    
    const response = await scheduleApi.get('', { params });
    return response.data.data;
  } catch (error) {
    console.error('Error fetching schedules:', error);
    throw error;
  }
};

/**
 * Get a schedule by ID
 */
export const getSchedule = async (scheduleId: string): Promise<Schedule> => {
  try {
    const response = await scheduleApi.get(`/${scheduleId}`);
    return response.data.data;
  } catch (error) {
    console.error(`Error fetching schedule ${scheduleId}:`, error);
    throw error;
  }
};

/**
 * Update a schedule
 */
export const updateSchedule = async (
  scheduleId: string,
  updates: Partial<Schedule>
): Promise<Schedule> => {
  try {
    const response = await scheduleApi.put(`/${scheduleId}`, updates);
    return response.data.data;
  } catch (error) {
    console.error(`Error updating schedule ${scheduleId}:`, error);
    throw error;
  }
};

/**
 * Delete a schedule
 */
export const deleteSchedule = async (scheduleId: string): Promise<void> => {
  try {
    await scheduleApi.delete(`/${scheduleId}`);
  } catch (error) {
    console.error(`Error deleting schedule ${scheduleId}:`, error);
    throw error;
  }
};

/**
 * Pause a schedule
 */
export const pauseSchedule = async (scheduleId: string): Promise<Schedule> => {
  try {
    const response = await scheduleApi.post(`/${scheduleId}/pause`);
    return response.data.data;
  } catch (error) {
    console.error(`Error pausing schedule ${scheduleId}:`, error);
    throw error;
  }
};

/**
 * Resume a schedule
 */
export const resumeSchedule = async (scheduleId: string): Promise<Schedule> => {
  try {
    const response = await scheduleApi.post(`/${scheduleId}/resume`);
    return response.data.data;
  } catch (error) {
    console.error(`Error resuming schedule ${scheduleId}:`, error);
    throw error;
  }
};

/**
 * Get execution logs for a schedule
 */
export const getExecutionLogs = async (
  scheduleId?: string,
  limit: number = 100
): Promise<ScheduleExecutionLog[]> => {
  try {
    const params: Record<string, string | number> = { limit };
    
    if (scheduleId) {
      params.schedule_id = scheduleId;
    }
    
    const response = await scheduleApi.get('/logs', { params });
    return response.data.data;
  } catch (error) {
    console.error('Error fetching execution logs:', error);
    throw error;
  }
};

/**
 * Get an execution log by ID
 */
export const getExecutionLog = async (logId: string): Promise<ScheduleExecutionLog> => {
  try {
    const response = await scheduleApi.get(`/logs/${logId}`);
    return response.data.data;
  } catch (error) {
    console.error(`Error fetching execution log ${logId}:`, error);
    throw error;
  }
};

/**
 * Clear execution logs
 */
export const clearExecutionLogs = async (
  scheduleId?: string,
  days?: number
): Promise<{ count: number }> => {
  try {
    const params: Record<string, string | number> = {};
    
    if (scheduleId) {
      params.schedule_id = scheduleId;
    }
    
    if (days) {
      params.days = days;
    }
    
    const response = await scheduleApi.delete('/logs', { params });
    return response.data.data;
  } catch (error) {
    console.error('Error clearing execution logs:', error);
    throw error;
  }
};

/**
 * Start the scheduler
 */
export const startScheduler = async (): Promise<void> => {
  try {
    await scheduleApi.post('/start-scheduler');
  } catch (error) {
    console.error('Error starting scheduler:', error);
    throw error;
  }
};

/**
 * Stop the scheduler
 */
export const stopScheduler = async (): Promise<void> => {
  try {
    await scheduleApi.post('/stop-scheduler');
  } catch (error) {
    console.error('Error stopping scheduler:', error);
    throw error;
  }
};

export default {
  createSchedule,
  getSchedules,
  getSchedule,
  updateSchedule,
  deleteSchedule,
  pauseSchedule,
  resumeSchedule,
  getExecutionLogs,
  getExecutionLog,
  clearExecutionLogs,
  startScheduler,
  stopScheduler,
};
