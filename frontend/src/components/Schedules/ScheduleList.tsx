import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Schedule, ScheduleStatus } from '../../types/schedule';
import { getSchedules, pauseSchedule, resumeSchedule, deleteSchedule } from '../../services/scheduleService';
import { formatDateTime } from '../../utils/dateUtils';

interface ScheduleListProps {
  workflowId?: string;
  onScheduleSelected?: (schedule: Schedule) => void;
}

const ScheduleList: React.FC<ScheduleListProps> = ({ workflowId, onScheduleSelected }) => {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<ScheduleStatus | ''>('');
  const [tagFilter, setTagFilter] = useState('');
  const [availableTags, setAvailableTags] = useState<string[]>([]);

  // Load schedules
  const loadSchedules = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await getSchedules(
        workflowId,
        statusFilter ? statusFilter : undefined,
        tagFilter || undefined
      );
      setSchedules(data);
      
      // Extract unique tags
      const tags = new Set<string>();
      data.forEach(schedule => {
        if (schedule.tags) {
          schedule.tags.forEach(tag => tags.add(tag));
        }
      });
      setAvailableTags(Array.from(tags));
    } catch (err: any) {
      setError(err.message || 'Failed to load schedules');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSchedules();
  }, [workflowId, statusFilter, tagFilter]);

  // Handle pause/resume
  const handleToggleStatus = async (schedule: Schedule) => {
    try {
      if (schedule.status === ScheduleStatus.ACTIVE) {
        await pauseSchedule(schedule.id);
      } else if (schedule.status === ScheduleStatus.PAUSED) {
        await resumeSchedule(schedule.id);
      }
      
      // Reload schedules
      loadSchedules();
    } catch (err: any) {
      setError(err.message || 'Failed to update schedule status');
    }
  };

  // Handle delete
  const handleDelete = async (scheduleId: string) => {
    if (!window.confirm('Are you sure you want to delete this schedule?')) {
      return;
    }
    
    try {
      await deleteSchedule(scheduleId);
      
      // Reload schedules
      loadSchedules();
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

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
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
      )}
      
      <div className="bg-gray-50 px-4 py-3 border-b border-gray-200 sm:px-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Schedules
          </h3>
          
          <div className="mt-3 sm:mt-0 sm:ml-4 flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
            <select
              className="block w-full sm:w-auto rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as ScheduleStatus | '')}
            >
              <option value="">All Statuses</option>
              <option value={ScheduleStatus.ACTIVE}>Active</option>
              <option value={ScheduleStatus.PAUSED}>Paused</option>
              <option value={ScheduleStatus.COMPLETED}>Completed</option>
              <option value={ScheduleStatus.FAILED}>Failed</option>
            </select>
            
            <select
              className="block w-full sm:w-auto rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              value={tagFilter}
              onChange={(e) => setTagFilter(e.target.value)}
            >
              <option value="">All Tags</option>
              {availableTags.map(tag => (
                <option key={tag} value={tag}>{tag}</option>
              ))}
            </select>
            
            <Link
              to={workflowId ? `/workflows/${workflowId}/schedules/new` : '/schedules/new'}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              New Schedule
            </Link>
          </div>
        </div>
      </div>
      
      {loading ? (
        <div className="px-4 py-5 sm:p-6 flex justify-center">
          <svg className="animate-spin h-8 w-8 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
      ) : schedules.length === 0 ? (
        <div className="px-4 py-5 sm:p-6 text-center text-gray-500">
          No schedules found.
        </div>
      ) : (
        <ul className="divide-y divide-gray-200">
          {schedules.map((schedule) => (
            <li key={schedule.id}>
              <div className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <p className="text-sm font-medium text-indigo-600 truncate">
                      {schedule.name}
                    </p>
                    <div className="ml-2 flex-shrink-0 flex">
                      <p className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeColor(schedule.status)}`}>
                        {schedule.status}
                      </p>
                    </div>
                  </div>
                  <div className="ml-2 flex-shrink-0 flex">
                    <button
                      onClick={() => handleToggleStatus(schedule)}
                      className="mr-2 inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      {schedule.status === ScheduleStatus.ACTIVE ? 'Pause' : 'Resume'}
                    </button>
                    
                    <Link
                      to={`/schedules/${schedule.id}`}
                      className="mr-2 inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Edit
                    </Link>
                    
                    <button
                      onClick={() => handleDelete(schedule.id)}
                      className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                    >
                      Delete
                    </button>
                  </div>
                </div>
                <div className="mt-2 sm:flex sm:justify-between">
                  <div className="sm:flex">
                    <p className="flex items-center text-sm text-gray-500">
                      {getScheduleTypeDisplay(schedule)}
                    </p>
                    <p className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0 sm:ml-6">
                      Executions: {schedule.execution_count}
                      {schedule.max_executions && ` / ${schedule.max_executions}`}
                    </p>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                    <p>
                      Next run: {schedule.next_execution_time ? formatDateTime(schedule.next_execution_time) : 'Not scheduled'}
                    </p>
                  </div>
                </div>
                {schedule.tags && schedule.tags.length > 0 && (
                  <div className="mt-2">
                    <div className="flex flex-wrap">
                      {schedule.tags.map(tag => (
                        <span key={tag} className="mr-2 mt-1 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ScheduleList;
