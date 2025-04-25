import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../../contexts/WebSocketContext';
import { ExecutionLog, NodeExecutionStatus, ExecutionStatus } from '../../types/execution';
import { formatDistanceToNow } from 'date-fns';

interface ConsoleWindowProps {
  executionId: string | null;
  isExecuting: boolean;
  onClose: () => void;
}

type ConsoleTab = 'execution' | 'logs' | 'results' | 'errors';

const ConsoleWindow: React.FC<ConsoleWindowProps> = ({
  executionId,
  isExecuting,
  onClose
}) => {
  const { subscribe, unsubscribe } = useWebSocket();
  const [activeTab, setActiveTab] = useState<ConsoleTab>('execution');
  const [logs, setLogs] = useState<ExecutionLog[]>([]);
  const [nodeStatuses, setNodeStatuses] = useState<Record<string, NodeExecutionStatus>>({});
  const [executionResult, setExecutionResult] = useState<any>(null);
  const [errors, setErrors] = useState<ExecutionLog[]>([]);
  const [isMinimized, setIsMinimized] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const consoleContentRef = useRef<HTMLDivElement>(null);

  // Subscribe to execution updates
  useEffect(() => {
    if (!executionId || !isExecuting) return;

    // Handler for execution logs
    const handleExecutionLog = (data: ExecutionLog) => {
      setLogs(prevLogs => [...prevLogs, data]);
      
      // Add to errors if it's an error
      if (data.status === 'error') {
        setErrors(prevErrors => [...prevErrors, data]);
      }
      
      // Auto-scroll to bottom
      if (autoScroll && consoleContentRef.current) {
        setTimeout(() => {
          if (consoleContentRef.current) {
            consoleContentRef.current.scrollTop = consoleContentRef.current.scrollHeight;
          }
        }, 50);
      }
    };

    // Handler for node status updates
    const handleNodeStatusUpdate = (data: any) => {
      const { node_id, status } = data;
      setNodeStatuses(prev => ({
        ...prev,
        [node_id]: status
      }));
    };

    // Handler for execution completion
    const handleExecutionCompleted = (data: any) => {
      setExecutionResult(data);
    };

    // Handler for execution error
    const handleExecutionError = (data: any) => {
      setExecutionResult(data);
      setErrors(prevErrors => [
        ...prevErrors,
        {
          node: 'workflow',
          status: 'error',
          value: data.error,
          timestamp: data.timestamp,
          traceback: data.traceback
        }
      ]);
    };

    // Subscribe to WebSocket events
    subscribe(`execution.${executionId}.log`, handleExecutionLog);
    subscribe(`execution.${executionId}.node_status`, handleNodeStatusUpdate);
    subscribe(`execution.${executionId}.completed`, handleExecutionCompleted);
    subscribe(`execution.${executionId}.error`, handleExecutionError);

    // Cleanup subscriptions
    return () => {
      unsubscribe(`execution.${executionId}.log`, handleExecutionLog);
      unsubscribe(`execution.${executionId}.node_status`, handleNodeStatusUpdate);
      unsubscribe(`execution.${executionId}.completed`, handleExecutionCompleted);
      unsubscribe(`execution.${executionId}.error`, handleExecutionError);
    };
  }, [executionId, isExecuting, subscribe, unsubscribe, autoScroll]);

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    } catch (e) {
      return timestamp;
    }
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'running':
        return 'text-blue-600';
      case 'error':
        return 'text-red-600';
      case 'pending':
        return 'text-yellow-600';
      default:
        return 'text-gray-600';
    }
  };

  // Clear console
  const clearConsole = () => {
    setLogs([]);
    setErrors([]);
  };

  // Export logs
  const exportLogs = () => {
    const exportData = {
      logs,
      nodeStatuses,
      executionResult,
      errors,
      executionId,
      timestamp: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `workflow-execution-${executionId}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className={`console-window fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 shadow-lg transition-all duration-300 z-50 ${isMinimized ? 'h-10' : 'h-80'}`}>
      {/* Console Header */}
      <div className="console-header flex items-center justify-between px-4 py-2 bg-gray-100 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          <span className="font-medium text-gray-700 dark:text-gray-300">
            {isExecuting ? (
              <span className="flex items-center">
                <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                Execution Console
              </span>
            ) : (
              'Execution Console'
            )}
          </span>
          {executionId && (
            <span className="text-xs text-gray-500 dark:text-gray-400">
              ID: {executionId.substring(0, 8)}...
            </span>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <button 
            onClick={clearConsole}
            className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            title="Clear console"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
          <button 
            onClick={exportLogs}
            className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            title="Export logs"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </button>
          <button 
            onClick={() => setIsMinimized(!isMinimized)}
            className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            title={isMinimized ? "Expand" : "Minimize"}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isMinimized ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"} />
            </svg>
          </button>
          <button 
            onClick={onClose}
            className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            title="Close console"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Console Tabs */}
      {!isMinimized && (
        <div className="console-tabs flex border-b border-gray-200 dark:border-gray-700">
          <button
            className={`px-4 py-2 text-sm font-medium ${activeTab === 'execution' ? 'text-blue-600 border-b-2 border-blue-600 dark:text-blue-400 dark:border-blue-400' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}`}
            onClick={() => setActiveTab('execution')}
          >
            Execution
          </button>
          <button
            className={`px-4 py-2 text-sm font-medium ${activeTab === 'logs' ? 'text-blue-600 border-b-2 border-blue-600 dark:text-blue-400 dark:border-blue-400' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}`}
            onClick={() => setActiveTab('logs')}
          >
            Logs {logs.length > 0 && `(${logs.length})`}
          </button>
          <button
            className={`px-4 py-2 text-sm font-medium ${activeTab === 'results' ? 'text-blue-600 border-b-2 border-blue-600 dark:text-blue-400 dark:border-blue-400' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}`}
            onClick={() => setActiveTab('results')}
          >
            Results
          </button>
          <button
            className={`px-4 py-2 text-sm font-medium ${activeTab === 'errors' ? 'text-blue-600 border-b-2 border-blue-600 dark:text-blue-400 dark:border-blue-400' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}`}
            onClick={() => setActiveTab('errors')}
          >
            Errors {errors.length > 0 && `(${errors.length})`}
          </button>
          <div className="ml-auto flex items-center px-4">
            <label className="flex items-center text-sm text-gray-500 dark:text-gray-400">
              <input
                type="checkbox"
                checked={autoScroll}
                onChange={() => setAutoScroll(!autoScroll)}
                className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              Auto-scroll
            </label>
          </div>
        </div>
      )}

      {/* Console Content */}
      {!isMinimized && (
        <div 
          ref={consoleContentRef}
          className="console-content overflow-auto h-[calc(100%-80px)] p-4 font-mono text-sm bg-white dark:bg-gray-800"
        >
          {activeTab === 'execution' && (
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Execution Overview</h3>
              
              {/* Execution Status */}
              <div className="bg-gray-50 dark:bg-gray-900 p-3 rounded-md">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Status:</span>
                    <span className={`ml-2 font-medium ${getStatusColor(executionResult?.status || 'running')}`}>
                      {executionResult?.status || (isExecuting ? 'Running' : 'Pending')}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Duration:</span>
                    <span className="ml-2 font-medium">
                      {executionResult?.execution_time_ms 
                        ? `${(executionResult.execution_time_ms / 1000).toFixed(2)}s` 
                        : 'Calculating...'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Start Time:</span>
                    <span className="ml-2">
                      {executionResult?.start_time 
                        ? formatTimestamp(executionResult.start_time)
                        : logs[0]?.timestamp 
                          ? formatTimestamp(logs[0].timestamp)
                          : 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">End Time:</span>
                    <span className="ml-2">
                      {executionResult?.end_time 
                        ? formatTimestamp(executionResult.end_time)
                        : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Node Execution Status */}
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mt-4 mb-2">Node Status</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-900">
                    <tr>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Node</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Status</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Duration</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Started</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {Object.entries(nodeStatuses).map(([nodeId, status]) => (
                      <tr key={nodeId}>
                        <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{nodeId}</td>
                        <td className="px-3 py-2 whitespace-nowrap text-sm">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(status.status)}`}>
                            {status.status}
                          </span>
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {status.execution_time_ms 
                            ? `${(status.execution_time_ms / 1000).toFixed(2)}s` 
                            : 'N/A'}
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {status.start_time 
                            ? formatTimestamp(status.start_time)
                            : 'N/A'}
                        </td>
                      </tr>
                    ))}
                    {Object.keys(nodeStatuses).length === 0 && (
                      <tr>
                        <td colSpan={4} className="px-3 py-2 text-sm text-gray-500 dark:text-gray-400 text-center">
                          No node execution data available
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'logs' && (
            <div className="space-y-1">
              {logs.length === 0 ? (
                <div className="text-center text-gray-500 dark:text-gray-400 py-4">
                  No logs available
                </div>
              ) : (
                logs.map((log, index) => (
                  <div 
                    key={index} 
                    className={`log-entry p-1 rounded ${log.status === 'error' ? 'bg-red-50 dark:bg-red-900/20' : ''}`}
                  >
                    <span className="text-gray-400 dark:text-gray-500 mr-2">[{formatTimestamp(log.timestamp)}]</span>
                    <span className={`font-medium ${getStatusColor(log.status)}`}>{log.node}:</span>
                    <span className="ml-2 text-gray-800 dark:text-gray-200">{log.value}</span>
                    {log.execution_time_ms && (
                      <span className="ml-2 text-gray-500 dark:text-gray-400">
                        ({(log.execution_time_ms / 1000).toFixed(2)}s)
                      </span>
                    )}
                    {log.cached && (
                      <span className="ml-2 text-blue-500 dark:text-blue-400 text-xs font-medium">
                        [CACHED]
                      </span>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'results' && (
            <div>
              {executionResult ? (
                <div className="space-y-4">
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Execution Results</h3>
                  
                  {/* Node Outputs */}
                  <div className="bg-gray-50 dark:bg-gray-900 p-3 rounded-md">
                    <h4 className="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase mb-2">Node Outputs</h4>
                    <pre className="text-xs overflow-auto max-h-40 p-2 bg-gray-100 dark:bg-gray-800 rounded">
                      {JSON.stringify(executionResult.node_outputs || {}, null, 2)}
                    </pre>
                  </div>
                  
                  {/* Execution Details */}
                  <div className="bg-gray-50 dark:bg-gray-900 p-3 rounded-md">
                    <h4 className="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase mb-2">Execution Details</h4>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Status:</span>
                        <span className={`ml-2 font-medium ${getStatusColor(executionResult.status)}`}>
                          {executionResult.status}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Duration:</span>
                        <span className="ml-2 font-medium">
                          {executionResult.execution_time_ms 
                            ? `${(executionResult.execution_time_ms / 1000).toFixed(2)}s` 
                            : 'N/A'}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Start Time:</span>
                        <span className="ml-2">
                          {executionResult.start_time 
                            ? formatTimestamp(executionResult.start_time)
                            : 'N/A'}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">End Time:</span>
                        <span className="ml-2">
                          {executionResult.end_time 
                            ? formatTimestamp(executionResult.end_time)
                            : 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-gray-500 dark:text-gray-400 py-4">
                  No results available yet
                </div>
              )}
            </div>
          )}

          {activeTab === 'errors' && (
            <div className="space-y-2">
              {errors.length === 0 ? (
                <div className="text-center text-gray-500 dark:text-gray-400 py-4">
                  No errors detected
                </div>
              ) : (
                errors.map((error, index) => (
                  <div key={index} className="bg-red-50 dark:bg-red-900/20 p-3 rounded-md">
                    <div className="flex items-start">
                      <div className="flex-shrink-0">
                        <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                          Error in {error.node}
                        </h3>
                        <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                          <p>{error.value}</p>
                        </div>
                        {error.traceback && (
                          <div className="mt-2">
                            <button
                              type="button"
                              className="text-xs text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
                              onClick={() => {
                                const el = document.getElementById(`traceback-${index}`);
                                if (el) {
                                  el.style.display = el.style.display === 'none' ? 'block' : 'none';
                                }
                              }}
                            >
                              Show/Hide Traceback
                            </button>
                            <pre
                              id={`traceback-${index}`}
                              className="mt-2 text-xs overflow-auto max-h-40 p-2 bg-red-100 dark:bg-red-900/40 rounded"
                              style={{ display: 'none' }}
                            >
                              {error.traceback}
                            </pre>
                          </div>
                        )}
                        <div className="mt-1 text-xs text-red-500 dark:text-red-400">
                          {formatTimestamp(error.timestamp)}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ConsoleWindow;
