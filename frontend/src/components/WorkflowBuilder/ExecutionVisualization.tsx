import React, { useState, useEffect } from 'react';
import { NodeData, Connection, ExecutionStatus, NodeExecutionStatus } from '../../types';
import { useWebSocket } from '../../contexts/WebSocketContext';
import './ExecutionVisualization.css';

interface ExecutionVisualizationProps {
  nodes: NodeData[];
  connections: Connection[];
  executionId: string | null;
  isExecuting: boolean;
}

interface DataFlowAnimation {
  connectionId: string;
  progress: number;
  data: any;
}

const ExecutionVisualization: React.FC<ExecutionVisualizationProps> = ({
  nodes,
  connections,
  executionId,
  isExecuting
}) => {
  const [nodeStatuses, setNodeStatuses] = useState<Record<string, NodeExecutionStatus>>({});
  const [dataFlows, setDataFlows] = useState<DataFlowAnimation[]>([]);
  const [executionLogs, setExecutionLogs] = useState<any[]>([]);
  const { subscribe, unsubscribe } = useWebSocket();

  // Subscribe to execution updates
  useEffect(() => {
    if (!executionId || !isExecuting) return;

    // Handler for node status updates
    const handleNodeStatusUpdate = (data: any) => {
      const { nodeId, status } = data;
      setNodeStatuses(prev => ({
        ...prev,
        [nodeId]: {
          ...prev[nodeId],
          ...status
        }
      }));
    };

    // Handler for data flow updates
    const handleDataFlowUpdate = (data: any) => {
      const { sourceNodeId, targetNodeId, sourcePort, targetPort, value } = data;
      
      // Find the connection
      const connection = connections.find(
        conn => 
          conn.from.nodeId === sourceNodeId && 
          conn.to.nodeId === targetNodeId &&
          conn.from.port === sourcePort &&
          conn.to.port === targetPort
      );

      if (connection) {
        // Add a new data flow animation
        const newFlow: DataFlowAnimation = {
          connectionId: connection.id,
          progress: 0,
          data: value
        };

        setDataFlows(prev => [...prev, newFlow]);
      }
    };

    // Handler for execution logs
    const handleExecutionLog = (data: any) => {
      setExecutionLogs(prev => [...prev, data]);
    };

    // Subscribe to WebSocket events
    subscribe(`execution.${executionId}.node_status`, handleNodeStatusUpdate);
    subscribe(`execution.${executionId}.data_flow`, handleDataFlowUpdate);
    subscribe(`execution.${executionId}.log`, handleExecutionLog);

    // Cleanup subscriptions
    return () => {
      unsubscribe(`execution.${executionId}.node_status`, handleNodeStatusUpdate);
      unsubscribe(`execution.${executionId}.data_flow`, handleDataFlowUpdate);
      unsubscribe(`execution.${executionId}.log`, handleExecutionLog);
    };
  }, [executionId, isExecuting, connections, subscribe, unsubscribe]);

  // Animate data flows
  useEffect(() => {
    if (!isExecuting || dataFlows.length === 0) return;

    const interval = setInterval(() => {
      setDataFlows(prev => {
        const updated = prev.map(flow => ({
          ...flow,
          progress: flow.progress + 0.02 // Increment progress
        }));

        // Remove completed animations
        return updated.filter(flow => flow.progress < 1);
      });
    }, 50);

    return () => clearInterval(interval);
  }, [isExecuting, dataFlows]);

  // Render node status overlays
  const renderNodeStatusOverlays = () => {
    return nodes.map(node => {
      const status = nodeStatuses[node.id] || { status: 'pending' };
      
      let statusClass = '';
      switch (status.status) {
        case 'running':
          statusClass = 'node-status-running';
          break;
        case 'completed':
          statusClass = 'node-status-completed';
          break;
        case 'failed':
          statusClass = 'node-status-failed';
          break;
        default:
          statusClass = 'node-status-pending';
      }

      return (
        <div
          key={`status-${node.id}`}
          className={`node-status-overlay ${statusClass}`}
          style={{
            left: `${node.x}px`,
            top: `${node.y}px`,
            width: `${node.width || 240}px`,
            height: `${node.height || 100}px`
          }}
        >
          {status.status === 'running' && (
            <div className="node-status-spinner"></div>
          )}
          {status.status === 'failed' && (
            <div className="node-status-error">
              <i className="fas fa-exclamation-triangle"></i>
            </div>
          )}
        </div>
      );
    });
  };

  // Render data flow animations
  const renderDataFlows = () => {
    return dataFlows.map((flow, index) => {
      const connection = connections.find(conn => conn.id === flow.connectionId);
      if (!connection) return null;

      const fromNode = nodes.find(n => n.id === connection.from.nodeId);
      const toNode = nodes.find(n => n.id === connection.to.nodeId);
      if (!fromNode || !toNode) return null;

      // Calculate position along the path
      const fromX = fromNode.x + (fromNode.width || 240);
      const fromY = fromNode.y + (fromNode.height || 100) / 2;
      const toX = toNode.x;
      const toY = toNode.y + (toNode.height || 100) / 2;

      // Interpolate position based on progress
      const x = fromX + (toX - fromX) * flow.progress;
      const y = fromY + (toY - fromY) * flow.progress;

      return (
        <div
          key={`flow-${index}`}
          className="data-flow-particle"
          style={{
            left: `${x}px`,
            top: `${y}px`
          }}
          title={JSON.stringify(flow.data, null, 2)}
        ></div>
      );
    });
  };

  if (!isExecuting) return null;

  return (
    <div className="execution-visualization-container">
      {renderNodeStatusOverlays()}
      {renderDataFlows()}
    </div>
  );
};

export default ExecutionVisualization;
