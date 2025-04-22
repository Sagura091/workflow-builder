import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getExecutionStatus, getExecutionState, resumeExecution, stopExecution } from '../../services/api';
import { ExecutionStatus, NodeExecutionStatus, ExecutionResult, WorkflowExecutionState } from '../../types/execution';
import { formatDateTime, formatDuration } from '../../utils/dateUtils';

interface ExecutionResultsProps {
  executionId?: string;
  onClose?: () => void;
}

const ExecutionResults: React.FC<ExecutionResultsProps> = ({ executionId: propExecutionId, onClose }) => {
  const params = useParams<{ executionId: string }>();
  const executionId = propExecutionId || params.executionId;
  
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);
  const [executionState, setExecutionState] = useState<WorkflowExecutionState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [resumeFromNodeId, setResumeFromNodeId] = useState<string>('');
  const [isResuming, setIsResuming] = useState(false);
  const [isStopping, setIsStopping] = useState(false);
  
  // Load execution results
  useEffect(() => {
    if (!executionId) return;
    
    const loadExecutionData = async () => {
      try {
        const [resultData, stateData] = await Promise.all([
          getExecutionStatus(executionId),
          getExecutionState(executionId)
        ]);
        
        setExecutionResult(resultData);
        setExecutionState(stateData);
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to load execution data');
      } finally {
        setLoading(false);
      }
    };
    
    loadExecutionData();
    
    // Set up polling for active executions
    const interval = setInterval(async () => {
      try {
        const stateData = await getExecutionState(executionId);
        setExecutionState(stateData);
        
        // If execution is no longer active, get the final results and stop polling
        if (stateData.status !== ExecutionStatus.RUNNING && stateData.status !== ExecutionStatus.PENDING) {
          const resultData = await getExecutionStatus(executionId);
          setExecutionResult(resultData);
          clearInterval(interval);
          setPollingInterval(null);
        }
      } catch (err) {
        console.error('Error polling execution state:', err);
      }
    }, 2000);
    
    setPollingInterval(interval);
    
    // Clean up polling on unmount
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [executionId]);
  
  // Handle resume execution
  const handleResume = async () => {
    if (!executionId || !resumeFromNodeId) return;
    
    setIsResuming(true);
    setError(null);
    
    try {
      await resumeExecution(executionId, resumeFromNodeId);
      
      // Reload execution state
      const stateData = await getExecutionState(executionId);
      setExecutionState(stateData);
      
      // Start polling again if not already polling
      if (!pollingInterval) {
        const interval = setInterval(async () => {
          try {
            const stateData = await getExecutionState(executionId);
            setExecutionState(stateData);
            
            // If execution is no longer active, get the final results and stop polling
            if (stateData.status !== ExecutionStatus.RUNNING && stateData.status !== ExecutionStatus.PENDING) {
              const resultData = await getExecutionStatus(executionId);
              setExecutionResult(resultData);
              clearInterval(interval);
              setPollingInterval(null);
            }
          } catch (err) {
            console.error('Error polling execution state:', err);
          }
        }, 2000);
        
        setPollingInterval(interval);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to resume execution');
    } finally {
      setIsResuming(false);
    }
  };
  
  // Handle stop execution
  const handleStop = async () => {
    if (!executionId) return;
    
    setIsStopping(true);
    setError(null);
    
    try {
      await stopExecution(executionId);
      
      // Reload execution state
      const stateData = await getExecutionState(executionId);
      setExecutionState(stateData);
    } catch (err: any) {
      setError(err.message || 'Failed to stop execution');
    } finally {
      setIsStopping(false);
    }
  };
  
  // Get status badge color
  const getStatusBadgeColor = (status: ExecutionStatus | NodeExecutionStatus) => {
    switch (status) {
      case ExecutionStatus.COMPLETED:
      case NodeExecutionStatus.COMPLETED:
        return 'bg-green-100 text-green-800';
      case ExecutionStatus.RUNNING:
      case NodeExecutionStatus.RUNNING:
        return 'bg-blue-100 text-blue-800';
      case ExecutionStatus.PENDING:
      case NodeExecutionStatus.PENDING:
        return 'bg-yellow-100 text-yellow-800';
      case ExecutionStatus.FAILED:
      case NodeExecutionStatus.FAILED:
        return 'bg-red-100 text-red-800';
      case ExecutionStatus.STOPPED:
        return 'bg-gray-100 text-gray-800';
      case ExecutionStatus.PAUSED:
        return 'bg-purple-100 text-purple-800';
      case NodeExecutionStatus.SKIPPED:
        return 'bg-gray-100 text-gray-800';
      case NodeExecutionStatus.CACHED:
        return 'bg-indigo-100 text-indigo-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  // Get node result
  const getNodeResult = (nodeId: string) => {
    if (!executionResult || !executionResult.node_results) return null;
    return executionResult.node_results[nodeId];
  };
  
  // Get node status
  const getNodeStatus = (nodeId: string) => {
    if (!executionState || !executionState.node_statuses) return null;
    return executionState.node_statuses[nodeId];
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
        </div>
      </div>
    );
  }
  
  if (!executionState) {
    return (
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Execution Not Found
          </h3>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
          <p className="text-sm text-gray-500">
            The requested execution could not be found.
          </p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
      <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
        <div>
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Execution Results
          </h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Execution ID: {executionId}
          </p>
        </div>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Close
          </button>
        )}
      </div>
      
      <div className="border-t border-gray-200">
        <dl>
          <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Status</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeColor(executionState.status)}`}>
                {executionState.status}
              </span>
              
              {/* Show action buttons based on status */}
              {executionState.status === ExecutionStatus.RUNNING && (
                <button
                  type="button"
                  onClick={handleStop}
                  disabled={isStopping}
                  className="ml-3 inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                >
                  {isStopping ? 'Stopping...' : 'Stop Execution'}
                </button>
              )}
              
              {executionState.status === ExecutionStatus.FAILED && (
                <div className="mt-2">
                  <label htmlFor="resume-node" className="block text-sm font-medium text-gray-700">
                    Resume from node:
                  </label>
                  <div className="mt-1 flex rounded-md shadow-sm">
                    <select
                      id="resume-node"
                      className="focus:ring-indigo-500 focus:border-indigo-500 flex-1 block w-full rounded-none rounded-l-md sm:text-sm border-gray-300"
                      value={resumeFromNodeId}
                      onChange={(e) => setResumeFromNodeId(e.target.value)}
                    >
                      <option value="">Select a node</option>
                      {Object.entries(executionState.node_statuses).map(([nodeId, status]) => (
                        <option key={nodeId} value={nodeId}>{nodeId}</option>
                      ))}
                    </select>
                    <button
                      type="button"
                      onClick={handleResume}
                      disabled={isResuming || !resumeFromNodeId}
                      className="inline-flex items-center px-3 py-2 border border-l-0 border-gray-300 rounded-r-md bg-gray-50 text-gray-500 sm:text-sm hover:bg-gray-100 disabled:opacity-50"
                    >
                      {isResuming ? 'Resuming...' : 'Resume'}
                    </button>
                  </div>
                </div>
              )}
            </dd>
          </div>
          
          <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Workflow</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              <Link
                to={`/workflows/${executionState.workflow_id}`}
                className="text-indigo-600 hover:text-indigo-900"
              >
                {executionState.workflow_id}
              </Link>
            </dd>
          </div>
          
          <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Execution Mode</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              {executionState.execution_mode}
              {executionState.execution_mode === 'partial' && executionState.selected_nodes && (
                <span className="ml-2 text-xs text-gray-500">
                  ({executionState.selected_nodes.length} selected nodes)
                </span>
              )}
              {executionState.execution_mode === 'resume' && executionState.resume_from_node && (
                <span className="ml-2 text-xs text-gray-500">
                  (resumed from {executionState.resume_from_node})
                </span>
              )}
            </dd>
          </div>
          
          <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Start Time</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              {formatDateTime(executionState.start_time)}
            </dd>
          </div>
          
          {executionState.end_time && (
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">End Time</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {formatDateTime(executionState.end_time)}
              </dd>
            </div>
          )}
          
          {executionState.execution_time_ms && (
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Execution Time</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {formatDuration(executionState.execution_time_ms / 1000)}
              </dd>
            </div>
          )}
        </dl>
      </div>
      
      {/* Node Results */}
      <div className="px-4 py-5 sm:px-6 border-t border-gray-200">
        <h3 className="text-lg leading-6 font-medium text-gray-900">
          Node Results
        </h3>
        <p className="mt-1 max-w-2xl text-sm text-gray-500">
          Results for each node in the workflow.
        </p>
      </div>
      
      <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Object.entries(executionState.node_statuses).map(([nodeId, status]) => {
            const nodeResult = getNodeResult(nodeId);
            
            return (
              <div
                key={nodeId}
                className={`border rounded-lg overflow-hidden ${selectedNodeId === nodeId ? 'ring-2 ring-indigo-500' : ''}`}
                onClick={() => setSelectedNodeId(nodeId)}
              >
                <div className="px-4 py-5 sm:px-6 bg-gray-50 flex justify-between items-center">
                  <h3 className="text-sm font-medium text-gray-900 truncate">
                    {nodeId}
                  </h3>
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeColor(status)}`}>
                    {status}
                    {nodeResult?.cached && (
                      <span className="ml-1">(cached)</span>
                    )}
                  </span>
                </div>
                <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
                  {nodeResult?.execution_time_ms && (
                    <p className="text-xs text-gray-500 mb-2">
                      Execution time: {formatDuration(nodeResult.execution_time_ms / 1000)}
                    </p>
                  )}
                  
                  {nodeResult?.error ? (
                    <div className="text-sm text-red-600 overflow-auto max-h-32">
                      {nodeResult.error}
                    </div>
                  ) : nodeResult?.outputs ? (
                    <div className="text-sm text-gray-900 overflow-auto max-h-32">
                      <pre className="whitespace-pre-wrap">
                        {JSON.stringify(nodeResult.outputs, null, 2)}
                      </pre>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No output available</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Execution Logs */}
      {executionResult?.log && executionResult.log.length > 0 && (
        <>
          <div className="px-4 py-5 sm:px-6 border-t border-gray-200">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Execution Logs
            </h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              Logs generated during workflow execution.
            </p>
          </div>
          
          <div className="border-t border-gray-200">
            <ul className="divide-y divide-gray-200">
              {executionResult.log.map((log, index) => (
                <li key={index} className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-indigo-600 truncate">
                      {log.node}
                    </p>
                    <div className="ml-2 flex-shrink-0 flex">
                      <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        {log.status || 'info'}
                      </p>
                    </div>
                  </div>
                  <div className="mt-2 sm:flex sm:justify-between">
                    <div className="sm:flex">
                      <p className="flex items-center text-sm text-gray-500">
                        {typeof log.value === 'object' ? JSON.stringify(log.value) : log.value}
                      </p>
                    </div>
                    <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                      <p>
                        {formatDateTime(log.timestamp)}
                      </p>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
};

export default ExecutionResults;
