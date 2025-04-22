import React, { useState, useEffect } from 'react';
import { Workflow } from '../../types';
import { ExecutionMode, WorkflowExecutionRequest } from '../../types/execution';
import { executeWorkflowAdvanced, executeWorkflowAsyncAdvanced, getExecutionStatus } from '../../services/api';
import { getCacheStats, getCacheableNodeTypes } from '../../services/cacheService';

interface AdvancedExecutionOptionsProps {
  workflow: Workflow;
  onExecutionStart: (executionId: string) => void;
  onClose: () => void;
}

const AdvancedExecutionOptions: React.FC<AdvancedExecutionOptionsProps> = ({
  workflow,
  onExecutionStart,
  onClose
}) => {
  const [executionMode, setExecutionMode] = useState<ExecutionMode>(ExecutionMode.FULL);
  const [selectedNodes, setSelectedNodes] = useState<string[]>([]);
  const [resumeFromNode, setResumeFromNode] = useState<string>('');
  const [previousExecutionId, setPreviousExecutionId] = useState<string>('');
  const [useCache, setUseCache] = useState<boolean>(true);
  const [isAsync, setIsAsync] = useState<boolean>(false);

  const [previousExecutions, setPreviousExecutions] = useState<string[]>([]);
  const [cacheStats, setCacheStats] = useState<any>(null);
  const [cacheableNodeTypes, setCacheableNodeTypes] = useState<string[]>([]);

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load cache stats and cacheable node types
  useEffect(() => {
    const loadCacheData = async () => {
      try {
        const stats = await getCacheStats();
        setCacheStats(stats);

        const nodeTypes = await getCacheableNodeTypes();
        setCacheableNodeTypes(nodeTypes);
      } catch (err) {
        console.error('Error loading cache data:', err);
      }
    };

    loadCacheData();
  }, []);

  // Load previous executions
  useEffect(() => {
    // This would be replaced with an actual API call to get previous executions
    // For now, we'll just use a placeholder
    setPreviousExecutions(['execution-1', 'execution-2', 'execution-3']);
  }, [workflow.id]);

  const handleNodeSelection = (nodeId: string) => {
    if (selectedNodes.includes(nodeId)) {
      setSelectedNodes(selectedNodes.filter(id => id !== nodeId));
    } else {
      setSelectedNodes([...selectedNodes, nodeId]);
    }
  };

  const handleExecute = async () => {
    setLoading(true);
    setError(null);

    try {
      // Create execution request
      const executionRequest: WorkflowExecutionRequest = {
        workflow: {
          id: workflow.id || undefined,
          name: workflow.name,
          nodes: workflow.nodes.map(node => ({
            id: node.id,
            type: node.type,
            config: node.config
          })),
          edges: workflow.connections.map(conn => ({
            source: conn.from.nodeId,
            target: conn.to.nodeId,
            source_port: conn.from.port,
            target_port: conn.to.port
          }))
        },
        execution_mode: executionMode,
        execution_options: {
          use_cache: useCache
        }
      };

      // Add mode-specific options
      if (executionMode === ExecutionMode.PARTIAL && selectedNodes.length > 0) {
        executionRequest.selected_nodes = selectedNodes;
      } else if (executionMode === ExecutionMode.RESUME) {
        if (resumeFromNode) {
          executionRequest.resume_from_node = resumeFromNode;
        }
        if (previousExecutionId) {
          executionRequest.previous_execution_id = previousExecutionId;
        }
      }

      // Execute workflow
      const response = isAsync
        ? await executeWorkflowAsyncAdvanced(executionRequest)
        : await executeWorkflowAdvanced(executionRequest);

      // Call onExecutionStart with the execution ID
      if (response.execution_id) {
        onExecutionStart(response.execution_id);
      }

      // Close the modal
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to execute workflow');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Advanced Execution Options</h3>
        </div>

        <div className="px-6 py-4">
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

          <div className="space-y-6">
            {/* Execution Mode */}
            <div>
              <label className="block text-sm font-medium text-gray-700">Execution Mode</label>
              <div className="mt-2 space-y-2">
                <div className="flex items-center">
                  <input
                    id="mode-full"
                    name="execution-mode"
                    type="radio"
                    className="h-4 w-4 text-indigo-600 border-gray-300 focus:ring-indigo-500"
                    checked={executionMode === ExecutionMode.FULL}
                    onChange={() => setExecutionMode(ExecutionMode.FULL)}
                  />
                  <label htmlFor="mode-full" className="ml-3 block text-sm font-medium text-gray-700">
                    Full Execution
                    <span className="block text-xs text-gray-500">Execute the entire workflow</span>
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    id="mode-partial"
                    name="execution-mode"
                    type="radio"
                    className="h-4 w-4 text-indigo-600 border-gray-300 focus:ring-indigo-500"
                    checked={executionMode === ExecutionMode.PARTIAL}
                    onChange={() => setExecutionMode(ExecutionMode.PARTIAL)}
                  />
                  <label htmlFor="mode-partial" className="ml-3 block text-sm font-medium text-gray-700">
                    Partial Execution
                    <span className="block text-xs text-gray-500">Execute only selected nodes and their dependencies</span>
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    id="mode-resume"
                    name="execution-mode"
                    type="radio"
                    className="h-4 w-4 text-indigo-600 border-gray-300 focus:ring-indigo-500"
                    checked={executionMode === ExecutionMode.RESUME}
                    onChange={() => setExecutionMode(ExecutionMode.RESUME)}
                  />
                  <label htmlFor="mode-resume" className="ml-3 block text-sm font-medium text-gray-700">
                    Resume Execution
                    <span className="block text-xs text-gray-500">Resume from a specific node or previous execution</span>
                  </label>
                </div>
              </div>
            </div>

            {/* Partial Execution Options */}
            {executionMode === ExecutionMode.PARTIAL && (
              <div>
                <label className="block text-sm font-medium text-gray-700">Select Nodes to Execute</label>
                <div className="mt-2 border border-gray-300 rounded-md p-2 max-h-60 overflow-y-auto">
                  {workflow.nodes.map(node => (
                    <div key={node.id} className="flex items-center py-1">
                      <input
                        id={`node-${node.id}`}
                        type="checkbox"
                        className="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                        checked={selectedNodes.includes(node.id)}
                        onChange={() => handleNodeSelection(node.id)}
                      />
                      <label htmlFor={`node-${node.id}`} className="ml-3 block text-sm text-gray-700">
                        {node.label || node.type}
                      </label>
                    </div>
                  ))}
                </div>
                {selectedNodes.length === 0 && (
                  <p className="mt-1 text-sm text-red-600">Please select at least one node</p>
                )}
              </div>
            )}

            {/* Resume Execution Options */}
            {executionMode === ExecutionMode.RESUME && (
              <div className="space-y-4">
                <div>
                  <label htmlFor="previous-execution" className="block text-sm font-medium text-gray-700">
                    Previous Execution (Optional)
                  </label>
                  <select
                    id="previous-execution"
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                    value={previousExecutionId}
                    onChange={(e) => setPreviousExecutionId(e.target.value)}
                  >
                    <option value="">Select a previous execution</option>
                    {previousExecutions.map(id => (
                      <option key={id} value={id}>{id}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="resume-node" className="block text-sm font-medium text-gray-700">
                    Resume From Node
                  </label>
                  <select
                    id="resume-node"
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                    value={resumeFromNode}
                    onChange={(e) => setResumeFromNode(e.target.value)}
                    required={executionMode === ExecutionMode.RESUME}
                  >
                    <option value="">Select a node</option>
                    {workflow.nodes.map(node => (
                      <option key={node.id} value={node.id}>{node.label || node.type}</option>
                    ))}
                  </select>
                  {executionMode === ExecutionMode.RESUME && !resumeFromNode && (
                    <p className="mt-1 text-sm text-red-600">Please select a node to resume from</p>
                  )}
                </div>
              </div>
            )}

            {/* Cache Options */}
            <div>
              <div className="flex items-center">
                <input
                  id="use-cache"
                  type="checkbox"
                  className="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                  checked={useCache}
                  onChange={(e) => setUseCache(e.target.checked)}
                />
                <label htmlFor="use-cache" className="ml-3 block text-sm font-medium text-gray-700">
                  Use Node Cache
                  <span className="block text-xs text-gray-500">Reuse results from previous executions when possible</span>
                </label>
              </div>

              {cacheStats && (
                <div className="mt-2 text-xs text-gray-500">
                  Cache stats: {cacheStats.size}/{cacheStats.max_size} entries, {cacheStats.hit_rate.toFixed(2)}% hit rate
                </div>
              )}
            </div>

            {/* Async Execution */}
            <div>
              <div className="flex items-center">
                <input
                  id="async-execution"
                  type="checkbox"
                  className="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                  checked={isAsync}
                  onChange={(e) => setIsAsync(e.target.checked)}
                />
                <label htmlFor="async-execution" className="ml-3 block text-sm font-medium text-gray-700">
                  Asynchronous Execution
                  <span className="block text-xs text-gray-500">Execute the workflow in the background</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div className="px-6 py-4 bg-gray-50 flex justify-end space-x-3 rounded-b-lg">
          <button
            type="button"
            className="py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            onClick={onClose}
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="button"
            className="py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-400"
            onClick={handleExecute}
            disabled={loading || (executionMode === ExecutionMode.PARTIAL && selectedNodes.length === 0) || (executionMode === ExecutionMode.RESUME && !resumeFromNode)}
          >
            {loading ? 'Executing...' : 'Execute Workflow'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdvancedExecutionOptions;
