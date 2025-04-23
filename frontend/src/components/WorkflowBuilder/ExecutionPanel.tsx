import React, { useState, useEffect } from 'react';
import { Workflow, NodeData, Connection } from '../../types';
import { executeWorkflow, stopExecution } from '../../services/api';
import { useWebSocket } from '../../contexts/WebSocketContext';
import ExecutionVisualization from './ExecutionVisualization';

interface ExecutionPanelProps {
  workflow: Workflow;
  nodes: NodeData[];
  connections: Connection[];
  onClose: () => void;
  onVisualizationChange: (isVisualizing: boolean, executionId: string | null) => void;
}

interface ExecutionStep {
  nodeId: string;
  nodeType: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime?: Date;
  endTime?: Date;
  duration?: string;
  details?: string;
}

const ExecutionPanel: React.FC<ExecutionPanelProps> = ({
  workflow,
  nodes,
  connections,
  onClose,
  onVisualizationChange
}) => {
  const { subscribe, unsubscribe } = useWebSocket();
  const [executionId, setExecutionId] = useState<string | null>(null);
  const [status, setStatus] = useState<'pending' | 'running' | 'completed' | 'failed'>('pending');
  const [steps, setSteps] = useState<ExecutionStep[]>([]);
  const [isExecuting, setIsExecuting] = useState(false);

  // Start execution when panel is shown
  useEffect(() => {
    startExecution();

    // Notify parent that visualization is active
    onVisualizationChange(true, executionId);

    return () => {
      // Notify parent that visualization is inactive when component unmounts
      onVisualizationChange(false, null);
    };
  }, []);

  // Start workflow execution
  const startExecution = async () => {
    try {
      setIsExecuting(true);
      setStatus('running');

      // Initialize steps based on workflow nodes
      const initialSteps = workflow.nodes.map(node => ({
        nodeId: node.id,
        nodeType: node.type,
        status: 'pending' as const
      }));
      setSteps(initialSteps);

      // Execute workflow
      const result = await executeWorkflow(workflow);
      const newExecutionId = result.executionId || '';
      setExecutionId(newExecutionId);

      // Notify parent of the execution ID
      onVisualizationChange(true, newExecutionId);

      // If WebSocket is not connected, fall back to simulation
      if (!subscribe) {
        console.warn('WebSocket not available, falling back to simulation');
        simulateExecution(initialSteps);
      } else {
        // Subscribe to execution status updates
        subscribe(`execution.${newExecutionId}.status`, handleExecutionStatusUpdate);
      }
    } catch (error) {
      console.error('Error executing workflow:', error);
      setStatus('failed');
      setIsExecuting(false);
    }
  };

  // Handle execution status updates from WebSocket
  const handleExecutionStatusUpdate = (data: any) => {
    const { status: newStatus, node_statuses } = data;

    setStatus(newStatus);

    if (newStatus === 'completed' || newStatus === 'failed') {
      setIsExecuting(false);
    }

    // Update steps based on node statuses
    if (node_statuses) {
      setSteps(prev => {
        return prev.map(step => {
          const nodeStatus = node_statuses[step.nodeId];
          if (!nodeStatus) return step;

          return {
            ...step,
            status: nodeStatus.status,
            startTime: nodeStatus.start_time ? new Date(nodeStatus.start_time) : undefined,
            endTime: nodeStatus.end_time ? new Date(nodeStatus.end_time) : undefined,
            duration: nodeStatus.duration ? `${(nodeStatus.duration / 1000).toFixed(2)}s` : undefined,
            details: nodeStatus.error || 'Execution successful'
          };
        });
      });
    }
  };

  // Stop workflow execution
  const handleStopExecution = async () => {
    if (!executionId) return;

    try {
      await stopExecution(executionId);
      setStatus('failed');
      setIsExecuting(false);

      // Unsubscribe from execution status updates
      unsubscribe(`execution.${executionId}.status`, handleExecutionStatusUpdate);

      // Update steps to show stopped status
      setSteps(prev => prev.map(step =>
        step.status === 'running' || step.status === 'pending'
          ? { ...step, status: 'failed', details: 'Execution stopped by user' }
          : step
      ));
    } catch (error) {
      console.error('Error stopping execution:', error);
    }
  };

  // Simulate execution progress (for demo purposes)
  const simulateExecution = (initialSteps: ExecutionStep[]) => {
    const totalSteps = initialSteps.length;
    let currentStep = 0;

    const interval = setInterval(() => {
      if (currentStep >= totalSteps) {
        clearInterval(interval);
        setStatus('completed');
        setIsExecuting(false);
        return;
      }

      // Update current step to running
      setSteps(prev => {
        const updated = [...prev];
        updated[currentStep] = {
          ...updated[currentStep],
          status: 'running',
          startTime: new Date()
        };
        return updated;
      });

      // After a delay, mark as completed and move to next step
      setTimeout(() => {
        setSteps(prev => {
          const updated = [...prev];
          const endTime = new Date();
          const startTime = updated[currentStep].startTime || new Date();
          const durationMs = endTime.getTime() - startTime.getTime();

          updated[currentStep] = {
            ...updated[currentStep],
            status: 'completed',
            endTime,
            duration: `${(durationMs / 1000).toFixed(2)}s`,
            details: 'Execution successful'
          };
          return updated;
        });

        currentStep++;
      }, 1500); // Simulate step execution time
    }, 2000); // Time between steps

    // Cleanup
    return () => clearInterval(interval);
  };

  // Get status badge class
  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 mt-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-700">Workflow Execution</h2>
        <button
          className="text-gray-500 hover:text-gray-700"
          onClick={onClose}
        >
          <i className="fas fa-times"></i>
        </button>
      </div>

      <div className="flex justify-between items-center mb-4">
        <div>
          <span className="text-sm font-medium text-gray-700">Status:</span>
          <span
            className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${getStatusBadgeClass(status)}`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </span>
        </div>
        <div>
          <button
            className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-sm disabled:opacity-50"
            onClick={handleStopExecution}
            disabled={!isExecuting}
          >
            <i className="fas fa-stop mr-1"></i> Stop Execution
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Step</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Duration</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Details</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {steps.map((step, index) => (
              <tr key={step.nodeId}>
                <td className="px-4 py-2 whitespace-nowrap">{index + 1}</td>
                <td className="px-4 py-2 whitespace-nowrap">{step.nodeType}</td>
                <td className="px-4 py-2 whitespace-nowrap">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadgeClass(step.status)}`}>
                    {step.status === 'running' ? (
                      <>
                        <i className="fas fa-spinner fa-spin mr-1"></i>
                        Running
                      </>
                    ) : (
                      step.status.charAt(0).toUpperCase() + step.status.slice(1)
                    )}
                  </span>
                </td>
                <td className="px-4 py-2 whitespace-nowrap">{step.duration || '-'}</td>
                <td className="px-4 py-2 whitespace-nowrap">{step.details || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ExecutionPanel;
