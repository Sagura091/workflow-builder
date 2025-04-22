import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { Schedule, ScheduleStatus, ScheduleExecutionLog } from '../../types/schedule';
import { getSchedule, getExecutionLogs, pauseSchedule, resumeSchedule, deleteSchedule } from '../../services/scheduleService';
import { getWorkflow } from '../../services/api';
import { Workflow } from '../../types';
import { formatDateTime, formatDuration } from '../../utils/dateUtils';

const ScheduleDetails: React.FC = () => {
  const { scheduleId } = useParams<{ scheduleId: string }>();
  const navigate = useNavigate();
  
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [executionLogs, setExecutionLogs] = useState<ScheduleExecutionLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Load schedule data
  useEffect(() => {
    const loadData = async () => {
      if (!scheduleId) return;
      
      setLoading(true);
      setError(null);
      
      try {
        // Load schedule
        const scheduleData = await getSchedule(scheduleId);
        setSchedule(scheduleData);
        
        // Load workflow
        const workflowData = await getWorkflow(scheduleData.workflow_id);
        setWorkflow(workflowData);
        
        // Load execution logs
        const logsData = await getExecutionLogs(scheduleId);
        setExecutionLogs(logsData);
      } catch (err: any) {
        setError(err.message || 'Failed to load schedule data');
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, [scheduleId]);
  
  // Handle pause/resume
  const handleToggleStatus = async () => {
    if (!schedule) return;
    
    try {
      if (schedule.status === ScheduleStatus.ACTIVE) {
        const updatedSchedule = await pauseSchedule(schedule.id);
        setSchedule(updatedSchedule);
      } else if (schedule.status === ScheduleStatus.PAUSED) {
        const updatedSchedule = await resumeSchedule(schedule.id);
        setSchedule(updatedSchedule);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to update schedule status');
    }
  };
  
  // Handle delete
  const handleDelete = async () => {
    if (!schedule) return;
    
    if (!window.confirm('Are you sure you want to delete this schedule?')) {
      return;
    }
    
    try {
      await deleteSchedule(schedule.id);
      navigate('/schedules');
    } catch (err: any) {
      setError(err.message || 'Failed to delete schedule');
    }
  };
  
  // Get status badge color
  const getStatusBadgeColor = (status: ScheduleStatus) => {
    switch (status) {
      case ScheduleStatus.ACTIVE:
        return 'bg-green-100 text-green-800';
      case ScheduleStatus.PAUSED:
        return 'bg-yellow-100 text-yellow-800';
      case ScheduleStatus.COMPLETED:
        return 'bg-blue-100 text-blue-800';
      case ScheduleStatus.FAILED:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  // Get execution status badge color
  const getExecutionStatusBadgeColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'success':
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'pending':
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'error':
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  // Get schedule type display
  const getScheduleTypeDisplay = (schedule: Schedule) => {
    switch (schedule.schedule_type) {
      case 'cron':
        return `Cron: ${schedule.cron_expression}`;
      case 'interval':
        return `Every ${schedule.interval_seconds} seconds`;
      case 'one_time':
        return `One time: ${formatDateTime(schedule.start_time)}`;
      case 'event':
        return 'Event-based';
      default:
        return 'Unknown';
    }
  };
  
  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <svg className="animate-spin h-8 w-8 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Error
          </h3>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
          <div className="bg-red-50 border-l-4 border-red-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
          <div className="mt-4">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Go Back
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  if (!schedule) {
    return (
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Schedule Not Found
          </h3>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
          <p className="text-sm text-gray-500">
            The requested schedule could not be found.
          </p>
          <div className="mt-4">
            <Link
              to="/schedules"
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Back to Schedules
            </Link>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
      <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
        <div>
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Schedule Details
          </h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Details and execution history for this schedule.
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            type="button"
            onClick={handleToggleStatus}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            {schedule.status === ScheduleStatus.ACTIVE ? 'Pause' : 'Resume'}
          </button>
          <Link
            to={`/schedules/${schedule.id}/edit`}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Edit
          </Link>
          <button
            type="button"
            onClick={handleDelete}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            Delete
          </button>
        </div>
      </div>
      
      <div className="border-t border-gray-200">
        <dl>
          <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Name</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{schedule.name}</dd>
          </div>
          
          <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Description</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              {schedule.description || 'No description provided'}
            </dd>
          </div>
          
          <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Workflow</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              {workflow ? (
                <Link
                  to={`/workflows/${workflow.id}`}
                  className="text-indigo-600 hover:text-indigo-900"
                >
                  {workflow.name}
                </Link>
              ) : (
                schedule.workflow_id
              )}
            </dd>
          </div>
          
          <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Status</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeColor(schedule.status)}`}>
                {schedule.status}
              </span>
            </dd>
          </div>
          
          <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Schedule Type</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              {getScheduleTypeDisplay(schedule)}
            </dd>
          </div>
          
          <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Next Execution</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              {schedule.next_execution_time ? formatDateTime(schedule.next_execution_time) : 'Not scheduled'}
            </dd>
          </div>
          
          <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Last Execution</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              {schedule.last_execution_time ? (
                <div>
                  {formatDateTime(schedule.last_execution_time)}
                  {schedule.last_execution_status && (
                    <span className={`ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getExecutionStatusBadgeColor(schedule.last_execution_status)}`}>
                      {schedule.last_execution_status}
                    </span>
                  )}
                </div>
              ) : (
                'Never executed'
              )}
            </dd>
          </div>
          
          <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Execution Count</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              {schedule.execution_count}
              {schedule.max_executions && ` / ${schedule.max_executions}`}
            </dd>
          </div>
          
          {schedule.start_time && (
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Start Time</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {formatDateTime(schedule.start_time)}
              </dd>
            </div>
          )}
          
          {schedule.end_time && (
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">End Time</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {formatDateTime(schedule.end_time)}
              </dd>
            </div>
          )}
          
          {schedule.tags && schedule.tags.length > 0 && (
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Tags</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="flex flex-wrap">
                  {schedule.tags.map(tag => (
                    <span key={tag} className="mr-2 mt-1 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                      {tag}
                    </span>
                  ))}
                </div>
              </dd>
            </div>
          )}
        </dl>
      </div>
      
      {/* Execution History */}
      <div className="px-4 py-5 sm:px-6 border-t border-gray-200">
        <h3 className="text-lg leading-6 font-medium text-gray-900">
          Execution History
        </h3>
        <p className="mt-1 max-w-2xl text-sm text-gray-500">
          Recent executions of this schedule.
        </p>
      </div>
      
      {executionLogs.length === 0 ? (
        <div className="px-4 py-5 sm:p-6 border-t border-gray-200 text-center text-gray-500">
          No execution history available.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Execution ID
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Start Time
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Duration
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {executionLogs.map((log) => (
                <tr key={log.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {log.execution_id.substring(0, 8)}...
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getExecutionStatusBadgeColor(log.status)}`}>
                      {log.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDateTime(log.start_time)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {log.duration_seconds ? formatDuration(log.duration_seconds) : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <Link
                      to={`/workflows/execution/${log.execution_id}`}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      View Results
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ScheduleDetails;
