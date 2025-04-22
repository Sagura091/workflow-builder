import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Schedule, ScheduleRequest, ScheduleType } from '../../types/schedule';
import { createSchedule, getSchedule, updateSchedule } from '../../services/scheduleService';
import { getWorkflow } from '../../services/api';
import { Workflow } from '../../types';

interface ScheduleFormProps {
  workflowId?: string;
  scheduleId?: string;
  onSuccess?: (schedule: Schedule) => void;
}

const ScheduleForm: React.FC<ScheduleFormProps> = ({ workflowId: propWorkflowId, scheduleId, onSuccess }) => {
  const navigate = useNavigate();
  const params = useParams();
  const workflowId = propWorkflowId || params.workflowId;
  const scheduleIdParam = scheduleId || params.scheduleId;
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  
  const [formData, setFormData] = useState<ScheduleRequest>({
    workflow_id: workflowId || '',
    name: '',
    description: '',
    schedule_type: ScheduleType.INTERVAL,
    interval_seconds: 3600, // Default to 1 hour
    tags: []
  });
  
  const [tagInput, setTagInput] = useState('');
  
  // Load schedule if editing
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Load workflow
        if (workflowId) {
          const workflowData = await getWorkflow(workflowId);
          setWorkflow(workflowData);
          setFormData(prev => ({ ...prev, workflow_id: workflowId }));
        }
        
        // Load schedule if editing
        if (scheduleIdParam) {
          const scheduleData = await getSchedule(scheduleIdParam);
          
          // Convert to form data
          setFormData({
            workflow_id: scheduleData.workflow_id,
            name: scheduleData.name,
            description: scheduleData.description || '',
            schedule_type: scheduleData.schedule_type,
            cron_expression: scheduleData.cron_expression,
            interval_seconds: scheduleData.interval_seconds,
            start_time: scheduleData.start_time,
            end_time: scheduleData.end_time,
            max_executions: scheduleData.max_executions,
            execution_options: scheduleData.execution_options,
            tags: scheduleData.tags || []
          });
          
          // Load workflow if not already loaded
          if (!workflowId) {
            const workflowData = await getWorkflow(scheduleData.workflow_id);
            setWorkflow(workflowData);
          }
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, [workflowId, scheduleIdParam]);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: value === '' ? undefined : Number(value)
    }));
  };
  
  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: value || undefined
    }));
  };
  
  const handleAddTag = () => {
    if (!tagInput.trim()) return;
    
    setFormData(prev => ({
      ...prev,
      tags: [...(prev.tags || []), tagInput.trim()]
    }));
    
    setTagInput('');
  };
  
  const handleRemoveTag = (tag: string) => {
    setFormData(prev => ({
      ...prev,
      tags: (prev.tags || []).filter(t => t !== tag)
    }));
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    setLoading(true);
    setError(null);
    
    try {
      let schedule: Schedule;
      
      if (scheduleIdParam) {
        // Update existing schedule
        schedule = await updateSchedule(scheduleIdParam, formData);
      } else {
        // Create new schedule
        schedule = await createSchedule(formData);
      }
      
      // Call success callback if provided
      if (onSuccess) {
        onSuccess(schedule);
      } else {
        // Navigate back to schedules list
        navigate(workflowId ? `/workflows/${workflowId}/schedules` : '/schedules');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save schedule');
    } finally {
      setLoading(false);
    }
  };
  
  if (loading && !formData.name) {
    return (
      <div className="flex justify-center py-8">
        <svg className="animate-spin h-8 w-8 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
    );
  }
  
  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
      <div className="px-4 py-5 sm:px-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">
          {scheduleIdParam ? 'Edit Schedule' : 'Create Schedule'}
        </h3>
        <p className="mt-1 max-w-2xl text-sm text-gray-500">
          {scheduleIdParam ? 'Update an existing schedule' : 'Create a new schedule for your workflow'}
        </p>
      </div>
      
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 mx-6 mb-4">
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
      
      <form onSubmit={handleSubmit}>
        <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
          <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            {/* Workflow */}
            <div className="sm:col-span-6">
              <label htmlFor="workflow_id" className="block text-sm font-medium text-gray-700">
                Workflow
              </label>
              <div className="mt-1">
                {workflow ? (
                  <div className="py-2 px-3 bg-gray-100 rounded-md">
                    {workflow.name}
                  </div>
                ) : (
                  <select
                    id="workflow_id"
                    name="workflow_id"
                    className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    value={formData.workflow_id}
                    onChange={handleChange}
                    required
                    disabled={!!workflowId || loading}
                  >
                    <option value="">Select a workflow</option>
                    {/* Workflow options would be loaded here */}
                  </select>
                )}
              </div>
            </div>
            
            {/* Name */}
            <div className="sm:col-span-6">
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Name
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  name="name"
                  id="name"
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  disabled={loading}
                />
              </div>
            </div>
            
            {/* Description */}
            <div className="sm:col-span-6">
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <div className="mt-1">
                <textarea
                  id="description"
                  name="description"
                  rows={3}
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  value={formData.description}
                  onChange={handleChange}
                  disabled={loading}
                />
              </div>
              <p className="mt-2 text-sm text-gray-500">
                Brief description of the schedule.
              </p>
            </div>
            
            {/* Schedule Type */}
            <div className="sm:col-span-3">
              <label htmlFor="schedule_type" className="block text-sm font-medium text-gray-700">
                Schedule Type
              </label>
              <div className="mt-1">
                <select
                  id="schedule_type"
                  name="schedule_type"
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  value={formData.schedule_type}
                  onChange={handleChange}
                  required
                  disabled={loading}
                >
                  <option value={ScheduleType.INTERVAL}>Interval</option>
                  <option value={ScheduleType.CRON}>Cron</option>
                  <option value={ScheduleType.ONE_TIME}>One Time</option>
                </select>
              </div>
            </div>
            
            {/* Schedule Details */}
            {formData.schedule_type === ScheduleType.INTERVAL && (
              <div className="sm:col-span-3">
                <label htmlFor="interval_seconds" className="block text-sm font-medium text-gray-700">
                  Interval (seconds)
                </label>
                <div className="mt-1">
                  <input
                    type="number"
                    name="interval_seconds"
                    id="interval_seconds"
                    min="1"
                    className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    value={formData.interval_seconds}
                    onChange={handleNumberChange}
                    required
                    disabled={loading}
                  />
                </div>
              </div>
            )}
            
            {formData.schedule_type === ScheduleType.CRON && (
              <div className="sm:col-span-3">
                <label htmlFor="cron_expression" className="block text-sm font-medium text-gray-700">
                  Cron Expression
                </label>
                <div className="mt-1">
                  <input
                    type="text"
                    name="cron_expression"
                    id="cron_expression"
                    className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    value={formData.cron_expression || ''}
                    onChange={handleChange}
                    placeholder="* * * * *"
                    required
                    disabled={loading}
                  />
                </div>
                <p className="mt-2 text-sm text-gray-500">
                  Format: minute hour day-of-month month day-of-week
                </p>
              </div>
            )}
            
            {formData.schedule_type === ScheduleType.ONE_TIME && (
              <div className="sm:col-span-3">
                <label htmlFor="start_time" className="block text-sm font-medium text-gray-700">
                  Execution Time
                </label>
                <div className="mt-1">
                  <input
                    type="datetime-local"
                    name="start_time"
                    id="start_time"
                    className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    value={formData.start_time || ''}
                    onChange={handleDateChange}
                    required
                    disabled={loading}
                  />
                </div>
              </div>
            )}
            
            {/* Start Time (for interval and cron) */}
            {(formData.schedule_type === ScheduleType.INTERVAL || formData.schedule_type === ScheduleType.CRON) && (
              <div className="sm:col-span-3">
                <label htmlFor="start_time" className="block text-sm font-medium text-gray-700">
                  Start Time (optional)
                </label>
                <div className="mt-1">
                  <input
                    type="datetime-local"
                    name="start_time"
                    id="start_time"
                    className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    value={formData.start_time || ''}
                    onChange={handleDateChange}
                    disabled={loading}
                  />
                </div>
              </div>
            )}
            
            {/* End Time */}
            <div className="sm:col-span-3">
              <label htmlFor="end_time" className="block text-sm font-medium text-gray-700">
                End Time (optional)
              </label>
              <div className="mt-1">
                <input
                  type="datetime-local"
                  name="end_time"
                  id="end_time"
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  value={formData.end_time || ''}
                  onChange={handleDateChange}
                  disabled={loading}
                />
              </div>
            </div>
            
            {/* Max Executions */}
            <div className="sm:col-span-3">
              <label htmlFor="max_executions" className="block text-sm font-medium text-gray-700">
                Max Executions (optional)
              </label>
              <div className="mt-1">
                <input
                  type="number"
                  name="max_executions"
                  id="max_executions"
                  min="1"
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  value={formData.max_executions || ''}
                  onChange={handleNumberChange}
                  disabled={loading}
                />
              </div>
            </div>
            
            {/* Tags */}
            <div className="sm:col-span-6">
              <label htmlFor="tags" className="block text-sm font-medium text-gray-700">
                Tags
              </label>
              <div className="mt-1 flex rounded-md shadow-sm">
                <input
                  type="text"
                  name="tagInput"
                  id="tagInput"
                  className="focus:ring-indigo-500 focus:border-indigo-500 flex-1 block w-full rounded-none rounded-l-md sm:text-sm border-gray-300"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  disabled={loading}
                  placeholder="Add a tag"
                />
                <button
                  type="button"
                  onClick={handleAddTag}
                  className="inline-flex items-center px-3 py-2 border border-l-0 border-gray-300 rounded-r-md bg-gray-50 text-gray-500 sm:text-sm hover:bg-gray-100"
                  disabled={loading || !tagInput.trim()}
                >
                  Add
                </button>
              </div>
              
              {formData.tags && formData.tags.length > 0 && (
                <div className="mt-2 flex flex-wrap">
                  {formData.tags.map(tag => (
                    <span key={tag} className="mr-2 mt-1 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                      {tag}
                      <button
                        type="button"
                        onClick={() => handleRemoveTag(tag)}
                        className="ml-1.5 inline-flex text-indigo-500 focus:outline-none"
                        disabled={loading}
                      >
                        <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="px-4 py-3 bg-gray-50 text-right sm:px-6">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="mr-3 inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            disabled={loading}
          >
            {loading ? 'Saving...' : (scheduleIdParam ? 'Update' : 'Create')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ScheduleForm;
