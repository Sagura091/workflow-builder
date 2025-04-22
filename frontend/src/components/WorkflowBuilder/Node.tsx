import React, { useRef, useEffect, useState } from 'react';
import { NodeData } from '../../types';
import { useNodeTypes, NodeTypePort } from '../../contexts/NodeTypesContext';
import { TYPE_COLORS } from '../../config';
import './NodeConnectors.css';
import './Node.css';

interface NodeProps {
  node: NodeData;
  isSelected: boolean;
  onSelect: () => void;
  onDelete: () => void;
  onEdit: () => void;
  onStartConnection: (nodeId: string, port: string, el: HTMLElement) => void;
  onEndConnection: (nodeId: string, port: string) => void;
  onUpdatePosition?: (nodeId: string, x: number, y: number) => void;
  onUpdateConfig?: (nodeId: string, config: Record<string, any>) => void;
}

const Node: React.FC<NodeProps> = ({
  node,
  isSelected,
  onSelect,
  onDelete,
  onEdit,
  onStartConnection,
  onEndConnection,
  onUpdatePosition,
  onUpdateConfig
}) => {
  // Custom drag implementation for smooth movement
  const nodeRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  // Track initial position and mouse position for dragging
  const dragState = useRef({
    startX: 0,
    startY: 0,
    initialX: node.x,
    initialY: node.y,
    isDragging: false
  });

  // Handle mouse down to start dragging
  const handleMouseDown = (e: React.MouseEvent) => {
    // Only handle left mouse button
    if (e.button !== 0) return;

    // Prevent default to avoid text selection
    e.preventDefault();
    e.stopPropagation();

    // Select the node
    onSelect();

    // Calculate offset from node position to mouse position
    const nodeRect = nodeRef.current?.getBoundingClientRect();
    if (!nodeRect) return;

    // Store initial positions
    dragState.current = {
      startX: e.clientX,
      startY: e.clientY,
      initialX: node.x,
      initialY: node.y,
      isDragging: true
    };

    setIsDragging(true);

    // Add global event listeners
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  // Handle mouse move during dragging
  const handleMouseMove = (e: MouseEvent) => {
    if (!dragState.current.isDragging) return;

    // Calculate new position
    const dx = e.clientX - dragState.current.startX;
    const dy = e.clientY - dragState.current.startY;

    const newX = dragState.current.initialX + dx;
    const newY = dragState.current.initialY + dy;

    // Update node position in real-time
    if (onUpdatePosition) {
      onUpdatePosition(node.id, newX, newY);
    }
  };

  // Handle mouse up to end dragging
  const handleMouseUp = (e: MouseEvent) => {
    if (!dragState.current.isDragging) return;

    // Reset dragging state
    dragState.current.isDragging = false;
    setIsDragging(false);

    // Remove global event listeners
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };

  // Clean up event listeners on unmount
  useEffect(() => {
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  // Get node type information
  const getNodeTypeInfo = (type: string) => {
    if (!type) {
      return { color: 'gray', icon: 'question', title: 'Unknown' };
    }

    // This would come from a context or props in a real implementation
    const nodeTypes: Record<string, { color: string, icon: string, title: string }> = {
      'core.begin': { color: 'green', icon: 'play', title: 'Begin' },
      'core.end': { color: 'red', icon: 'stop', title: 'End' },
      'core.text_input': { color: 'blue', icon: 'font', title: 'Text Input' },
      'core.text_output': { color: 'red', icon: 'comment', title: 'Text Output' },
      'core.for_loop': { color: 'purple', icon: 'sync', title: 'For Loop' },
      'core.while_loop': { color: 'purple', icon: 'sync-alt', title: 'While Loop' },
      'core.compare': { color: 'orange', icon: 'equals', title: 'Compare' },
      'core.set_variable': { color: 'blue', icon: 'database', title: 'Set Variable' },
      'core.get_variable': { color: 'green', icon: 'database', title: 'Get Variable' },
      'core.conditional': { color: 'orange', icon: 'code-branch', title: 'Conditional' },
      'core.switch': { color: 'purple', icon: 'random', title: 'Switch' },
      'core.delay': { color: 'gray', icon: 'clock', title: 'Delay' },
      'core.random_generator': { color: 'teal', icon: 'dice', title: 'Random Generator' },
      'core.http_request': { color: 'blue', icon: 'globe', title: 'HTTP Request' },
      // Plugins
      'http_request': { color: 'red', icon: 'globe', title: 'HTTP Request' },
      'json_parser': { color: 'blue', icon: 'code', title: 'JSON Parser' },
      'csv_parser': { color: 'green', icon: 'table', title: 'CSV Parser' },
      // Legacy nodes
      'data_loader': { color: 'blue', icon: 'database', title: 'Data Loader' },
      'data_transform': { color: 'green', icon: 'filter', title: 'Data Transform' },
      'feature_engineering': { color: 'purple', icon: 'cogs', title: 'Feature Engineering' },
      'train_model': { color: 'red', icon: 'brain', title: 'Train Model' },
      'evaluate': { color: 'indigo', icon: 'chart-line', title: 'Evaluate' },
      'predict': { color: 'amber', icon: 'magic', title: 'Predict' },
      'deploy_model': { color: 'blue', icon: 'rocket', title: 'Deploy Model' },
      'monitoring': { color: 'red', icon: 'heartbeat', title: 'Monitoring' }
    };

    // If the type is not in our predefined list, try to extract a friendly name
    if (!nodeTypes[type]) {
      // For types like 'core.something', extract 'Something'
      const parts = type.split('.');
      if (parts.length > 1) {
        const lastPart = parts[parts.length - 1];
        // Convert snake_case to Title Case
        const title = lastPart
          .split('_')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');
        return { color: 'gray', icon: 'cube', title };
      }
    }

    return nodeTypes[type] || { color: 'gray', icon: 'question', title: type };
  };

  const { color, icon, title } = getNodeTypeInfo(node?.type || '');

  // Handle node click
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onSelect();
  };

  // Handle input/output point mouse events
  const handleInputPointMouseDown = (e: React.MouseEvent, port: string) => {
    // Only handle left mouse button
    if (e.button !== 0) return;

    e.stopPropagation();
    console.log(`Input point mousedown: ${port} on node ${node.id}`);
    onEndConnection(node.id, port);
  };

  const handleOutputPointMouseDown = (e: React.MouseEvent, port: string) => {
    // Only handle left mouse button
    if (e.button !== 0) return;

    e.stopPropagation();
    console.log(`Output point mousedown: ${port} on node ${node.id}`);
    if (e.currentTarget instanceof HTMLElement) {
      onStartConnection(node.id, port, e.currentTarget);
    }
  };

  // Handle mouse over for connection points
  const handlePortMouseOver = (e: React.MouseEvent, portType: 'input' | 'output', port: string, dataType: string) => {
    const el = e.currentTarget as HTMLElement;
    el.style.transform = 'translate(-50%, -50%) scale(1.5)';
    el.style.boxShadow = '0 0 10px 2px rgba(59, 130, 246, 0.7)';
    el.style.zIndex = '30';

    // Show port label
    const label = el.querySelector('.port-label') as HTMLElement;
    if (label) {
      label.style.opacity = '1';
    }

    // Create or update port hover indicator
    let indicator = document.querySelector('.port-hover-indicator') as HTMLElement;
    if (!indicator) {
      indicator = document.createElement('div');
      indicator.className = 'port-hover-indicator';
      document.body.appendChild(indicator);
    }

    // Set indicator content and position
    indicator.textContent = `${port} (${dataType})`;
    indicator.setAttribute('data-type', dataType);
    indicator.classList.add('visible');

    // Position the indicator near the port
    const rect = el.getBoundingClientRect();
    indicator.style.left = `${portType === 'input' ? rect.left - 10 : rect.right + 10}px`;
    indicator.style.top = `${rect.top}px`;
    indicator.style.transform = `translateY(-50%)`;
  };

  // Handle mouse out for connection points
  const handlePortMouseOut = (e: React.MouseEvent) => {
    const el = e.currentTarget as HTMLElement;
    el.style.transform = 'translate(-50%, -50%)';
    el.style.boxShadow = '0 0 8px 0 rgba(59, 130, 246, 0.8)';
    el.style.zIndex = '10';

    // Hide port label
    const label = el.querySelector('.port-label') as HTMLElement;
    if (label) {
      label.style.opacity = '0';
    }

    // Hide port hover indicator
    const indicator = document.querySelector('.port-hover-indicator');
    if (indicator) {
      indicator.classList.remove('visible');
    }
  };

  // Get node types from context
  let nodeTypes: Record<string, { inputs: Array<{id: string, name: string, type: string, ui_properties?: any}>, outputs: Array<{id: string, name: string, type: string, ui_properties?: any}> }> = {};
  try {
    const context = useNodeTypes();
    nodeTypes = context.nodeTypes as Record<string, { inputs: Array<{id: string, name: string, type: string, ui_properties?: any}>, outputs: Array<{id: string, name: string, type: string, ui_properties?: any}> }>;
  } catch (error) {
    console.warn('NodeTypesContext not available, using fallback values');
  }

  // Get node inputs and outputs
  const getNodePorts = (type: string) => {
    if (!type) {
      console.warn('No node type provided');
      return { inputs: [], outputs: [] };
    }

    // First try to get from the context
    if (nodeTypes && nodeTypes[type]) {
      console.log(`Found node type ${type} in context:`, nodeTypes[type]);
      return nodeTypes[type];
    }

    console.warn(`Node type ${type} not found in context, using fallback`);

    // Fallback to hardcoded values if not found in context
    const nodePorts: Record<string, { inputs: Array<{id: string, name: string, type: string, ui_properties?: any}>, outputs: Array<{id: string, name: string, type: string, ui_properties?: any}> }> = {
      // Default node types with inputs and outputs
      'default': {
        inputs: [
          { id: 'input1', name: 'Input 1', type: 'any', ui_properties: { position: 'left-top' } },
          { id: 'input2', name: 'Input 2', type: 'any', ui_properties: { position: 'left-bottom' } }
        ],
        outputs: [
          { id: 'output1', name: 'Output 1', type: 'any', ui_properties: { position: 'right-top' } },
          { id: 'output2', name: 'Output 2', type: 'any', ui_properties: { position: 'right-bottom' } }
        ]
      },
      'core.begin': {
        inputs: [],
        outputs: [
          { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'right-top' } },
          { id: 'workflow_id', name: 'Workflow ID', type: 'string', ui_properties: { position: 'right-center' } },
          { id: 'timestamp', name: 'Timestamp', type: 'number', ui_properties: { position: 'right-bottom' } }
        ]
      },
      'core.end': {
        inputs: [
          { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'left-top' } },
          { id: 'result', name: 'Result', type: 'any', ui_properties: { position: 'left-center' } }
        ],
        outputs: [
          { id: 'workflow_id', name: 'Workflow ID', type: 'string', ui_properties: { position: 'right-top' } },
          { id: 'execution_time', name: 'Execution Time', type: 'number', ui_properties: { position: 'right-center' } }
        ]
      },
      'core.for_loop': {
        inputs: [
          { id: 'items', name: 'Items', type: 'array', ui_properties: { position: 'left-top' } },
          { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'left-center' } }
        ],
        outputs: [
          { id: 'completed', name: 'Completed', type: 'trigger', ui_properties: { position: 'right-top' } },
          { id: 'current_item', name: 'Current Item', type: 'any', ui_properties: { position: 'right-center' } },
          { id: 'index', name: 'Index', type: 'number', ui_properties: { position: 'right-bottom' } }
        ]
      },
      'core.while_loop': {
        inputs: [
          { id: 'condition', name: 'Condition', type: 'boolean', ui_properties: { position: 'left-top' } },
          { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'left-center' } }
        ],
        outputs: [
          { id: 'completed', name: 'Completed', type: 'trigger', ui_properties: { position: 'right-top' } },
          { id: 'iteration', name: 'Iteration', type: 'trigger', ui_properties: { position: 'right-center' } },
          { id: 'iteration_count', name: 'Iteration Count', type: 'number', ui_properties: { position: 'right-bottom' } }
        ]
      },
      'core.compare': {
        inputs: [
          { id: 'value_a', name: 'Value A', type: 'any', ui_properties: { position: 'left-top' } },
          { id: 'value_b', name: 'Value B', type: 'any', ui_properties: { position: 'left-center' } },
          { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'left-bottom' } }
        ],
        outputs: [
          { id: 'result', name: 'Result', type: 'boolean', ui_properties: { position: 'right-top' } },
          { id: 'true_output', name: 'True', type: 'trigger', ui_properties: { position: 'right-center' } },
          { id: 'false_output', name: 'False', type: 'trigger', ui_properties: { position: 'right-bottom' } }
        ]
      },
      'core.conditional': {
        inputs: [
          { id: 'condition', name: 'Condition', type: 'boolean', ui_properties: { position: 'left-top' } },
          { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'left-bottom' } }
        ],
        outputs: [
          { id: 'true_branch', name: 'True', type: 'trigger', ui_properties: { position: 'right-top' } },
          { id: 'false_branch', name: 'False', type: 'trigger', ui_properties: { position: 'right-bottom' } }
        ]
      },
      'core.switch': {
        inputs: [
          { id: 'value', name: 'Value', type: 'any', ui_properties: { position: 'left-top' } },
          { id: 'cases', name: 'Cases', type: 'array', ui_properties: { position: 'left-center' } },
          { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'left-bottom' } }
        ],
        outputs: [
          { id: 'case_1', name: 'Case 1', type: 'trigger', ui_properties: { position: 'right-top' } },
          { id: 'case_2', name: 'Case 2', type: 'trigger', ui_properties: { position: 'right-center' } },
          { id: 'default', name: 'Default', type: 'trigger', ui_properties: { position: 'right-bottom' } },
          { id: 'selected_case', name: 'Selected Case', type: 'string', ui_properties: { position: 'right-bottom' } }
        ]
      },
      'core.delay': {
        inputs: [
          { id: 'duration', name: 'Duration (ms)', type: 'number', ui_properties: { position: 'left-top' } },
          { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'left-bottom' } }
        ],
        outputs: [
          { id: 'completed', name: 'Completed', type: 'trigger', ui_properties: { position: 'right-top' } }
        ]
      },
      'core.random_generator': {
        inputs: [
          { id: 'min', name: 'Min', type: 'number', ui_properties: { position: 'left-top' } },
          { id: 'max', name: 'Max', type: 'number', ui_properties: { position: 'left-center' } },
          { id: 'type', name: 'Type', type: 'string', ui_properties: { position: 'left-center' } },
          { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'left-bottom' } }
        ],
        outputs: [
          { id: 'value', name: 'Value', type: 'any', ui_properties: { position: 'right-top' } },
          { id: 'completed', name: 'Completed', type: 'trigger', ui_properties: { position: 'right-bottom' } }
        ]
      },
      'core.http_request': {
        inputs: [
          { id: 'url', name: 'URL', type: 'string', ui_properties: { position: 'left-top' } },
          { id: 'method', name: 'Method', type: 'string', ui_properties: { position: 'left-center' } },
          { id: 'headers', name: 'Headers', type: 'object', ui_properties: { position: 'left-center' } },
          { id: 'body', name: 'Body', type: 'any', ui_properties: { position: 'left-bottom' } },
          { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'left-bottom' } }
        ],
        outputs: [
          { id: 'response', name: 'Response', type: 'any', ui_properties: { position: 'right-top' } },
          { id: 'status', name: 'Status', type: 'number', ui_properties: { position: 'right-center' } },
          { id: 'error', name: 'Error', type: 'string', ui_properties: { position: 'right-bottom' } },
          { id: 'completed', name: 'Completed', type: 'trigger', ui_properties: { position: 'right-bottom' } }
        ]
      },
      'core.text_input': {
        inputs: [
          { id: 'variables', name: 'Variables', type: 'object', ui_properties: { position: 'left-center' } },
          { id: 'override', name: 'Override', type: 'string', ui_properties: { position: 'left-bottom' } }
        ],
        outputs: [
          { id: 'text', name: 'Text', type: 'string', ui_properties: { position: 'right-top' } },
          { id: 'length', name: 'Length', type: 'number', ui_properties: { position: 'right-center' } },
          { id: 'is_empty', name: 'Is Empty', type: 'boolean', ui_properties: { position: 'right-bottom' } }
        ]
      },
      'core.text_output': {
        inputs: [
          { id: 'text', name: 'Text', type: 'string', ui_properties: { position: 'left-top' } },
          { id: 'label', name: 'Label', type: 'string', ui_properties: { position: 'left-center' } },
          { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'left-bottom' } }
        ],
        outputs: [
          { id: 'text', name: 'Text', type: 'string', ui_properties: { position: 'right-top' } },
          { id: 'length', name: 'Length', type: 'number', ui_properties: { position: 'right-center' } }
        ]
      },
      // Plugin nodes
      'http_request': {
        inputs: [
          { id: 'url', name: 'URL', type: 'string', ui_properties: { position: 'left-top' } },
          { id: 'method', name: 'Method', type: 'string', ui_properties: { position: 'left-center' } },
          { id: 'headers', name: 'Headers', type: 'object', ui_properties: { position: 'left-center' } },
          { id: 'body', name: 'Body', type: 'any', ui_properties: { position: 'left-bottom' } },
          { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'left-bottom' } }
        ],
        outputs: [
          { id: 'response', name: 'Response', type: 'any', ui_properties: { position: 'right-top' } },
          { id: 'status', name: 'Status', type: 'number', ui_properties: { position: 'right-center' } },
          { id: 'error', name: 'Error', type: 'string', ui_properties: { position: 'right-bottom' } }
        ]
      },
      'json_parser': {
        inputs: [
          { id: 'input', name: 'Input', type: 'string', ui_properties: { position: 'left-top' } },
          { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'left-bottom' } }
        ],
        outputs: [
          { id: 'output', name: 'Output', type: 'object', ui_properties: { position: 'right-top' } },
          { id: 'error', name: 'Error', type: 'string', ui_properties: { position: 'right-bottom' } }
        ]
      },
      'csv_parser': {
        inputs: [
          { id: 'input', name: 'Input', type: 'string', ui_properties: { position: 'left-top' } },
          { id: 'has_header', name: 'Has Header', type: 'boolean', ui_properties: { position: 'left-center' } },
          { id: 'delimiter', name: 'Delimiter', type: 'string', ui_properties: { position: 'left-center' } },
          { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'left-bottom' } }
        ],
        outputs: [
          { id: 'output', name: 'Output', type: 'array', ui_properties: { position: 'right-top' } },
          { id: 'headers', name: 'Headers', type: 'array', ui_properties: { position: 'right-center' } },
          { id: 'error', name: 'Error', type: 'string', ui_properties: { position: 'right-bottom' } }
        ]
      },
      // Legacy nodes for backward compatibility
      data_loader: {
        inputs: [],
        outputs: [{ id: 'data', name: 'data', type: 'dataset' }]
      },
      data_transform: {
        inputs: [{ id: 'data', name: 'data', type: 'dataset' }],
        outputs: [{ id: 'transformed_data', name: 'transformed_data', type: 'dataset' }]
      }
    };

    // Try to get the specific node type, or fall back to the default type, or empty arrays as a last resort
    const result = nodePorts[type] || nodePorts['default'] || { inputs: [], outputs: [] };
    console.log(`Using node ports for ${type}:`, result);
    return result;
  };

  const { inputs, outputs } = getNodePorts(node?.type || '');

  // Debug node ports
  console.log(`Node ${node?.id} (${node?.type}) ports:`, { inputs, outputs });

  // Get port positions based on the number of ports and UI properties
  const getPortPositions = (ports: Array<{id?: string, name: string, type: string, ui_properties?: any}>, side: 'left' | 'right') => {
    if (!ports || !Array.isArray(ports)) {
      console.warn(`No ports provided for ${side} side of node ${node?.id}`);
      return [];
    }

    if (ports.length === 0) {
      console.log(`No ${side} ports for node ${node?.id}`);
      return [];
    }

    // Get actual node height from DOM element or use default
    const nodeEl = nodeRef.current;
    const nodeHeight = nodeEl ? nodeEl.clientHeight : 100;
    const spacing = nodeHeight / (ports.length + 1);

    return ports.map((port, index) => {
      // Check if port has UI position property
      let position = '';
      if (port.ui_properties && port.ui_properties.position) {
        position = port.ui_properties.position;
      }

      // Calculate y position based on UI property or default spacing
      let y = spacing * (index + 1);

      if (position) {
        if (position.includes('top')) {
          y = 20;
        } else if (position.includes('center')) {
          y = nodeHeight / 2;
        } else if (position.includes('bottom')) {
          y = nodeHeight - 20;
        }
      }

      // Ensure port has an id
      const portId = port.id || port.name;

      // Add more debug information
      console.debug(`Port ${portId} (${port.type}) positioned at y=${y} on ${side} side of node ${node.id}`);

      return { ...port, id: portId, y };
    });
  };

  const [inputPositions, setInputPositions] = useState(getPortPositions(inputs, 'left'));
  const [outputPositions, setOutputPositions] = useState(getPortPositions(outputs, 'right'));

  // Update port positions when node size changes or inputs/outputs change
  useEffect(() => {
    setInputPositions(getPortPositions(inputs, 'left'));
    setOutputPositions(getPortPositions(outputs, 'right'));
  }, [inputs, outputs, node.width, node.height, node.id, node.type]);

  // Use ResizeObserver to detect size changes
  useEffect(() => {
    if (!nodeRef.current) return;

    const resizeObserver = new ResizeObserver(() => {
      setInputPositions(getPortPositions(inputs, 'left'));
      setOutputPositions(getPortPositions(outputs, 'right'));
    });

    resizeObserver.observe(nodeRef.current);

    return () => {
      resizeObserver.disconnect();
    };
  }, [inputs, outputs, node.id]);

  // Get node configuration summary with inline editing
  const getConfigSummary = () => {
    if (!node.config || Object.keys(node.config).length === 0) {
      return (
        <div className="text-gray-500 italic text-center">
          <i className="fas fa-cog mr-1"></i>
          Configure this node...
        </div>
      );
    }

    // Function to handle inline config changes
    const handleInlineConfigChange = (key: string, newValue: any) => {
      const updatedConfig = {
        ...node.config,
        [key]: newValue
      };

      // Call the parent's onUpdateConfig function to update the node
      if (onUpdateConfig) {
        onUpdateConfig(node.id, updatedConfig);
      }
    };

    return Object.entries(node.config).map(([key, value]) => {
      // Determine the input type based on the value type
      const valueType = Array.isArray(value) ? 'array' : typeof value;

      // Render different input types based on the value type
      let inputElement;
      switch (valueType) {
        case 'boolean':
          inputElement = (
            <input
              type="checkbox"
              checked={!!value}
              onChange={(e) => handleInlineConfigChange(key, e.target.checked)}
              className="h-4 w-4 text-blue-600 rounded"
              onClick={(e) => e.stopPropagation()}
            />
          );
          break;
        case 'number':
          inputElement = (
            <input
              type="number"
              value={value as number}
              onChange={(e) => handleInlineConfigChange(key, parseFloat(e.target.value))}
              className="w-20 border rounded-sm px-1 py-0 text-xs"
              onClick={(e) => e.stopPropagation()}
            />
          );
          break;
        case 'array':
          const displayValue = (value as any[]).join(', ');
          inputElement = (
            <span className="ml-2 truncate max-w-[100px] text-gray-600">{displayValue}</span>
          );
          break;
        default: // string or other types
          if (String(value).length > 20) {
            inputElement = (
              <span className="ml-2 truncate max-w-[100px] text-gray-600">{String(value).substring(0, 20)}...</span>
            );
          } else {
            inputElement = (
              <input
                type="text"
                value={String(value)}
                onChange={(e) => handleInlineConfigChange(key, e.target.value)}
                className="w-24 border rounded-sm px-1 py-0 text-xs"
                onClick={(e) => e.stopPropagation()}
              />
            );
          }
      }

      return (
        <div key={key} className="flex justify-between items-center mb-2 text-xs">
          <span className="font-medium text-gray-700">{key}:</span>
          {inputElement}
        </div>
      );
    });
  };

  return (
    <div
      ref={nodeRef}
      className={`workflow-node w-56 ${isSelected ? 'selected' : ''} ${isDragging ? 'dragging' : ''}`}
      style={{
        left: `${node.x}px`,
        top: `${node.y}px`,
        borderWidth: '2px',
        borderStyle: 'solid',
        borderColor: `var(--node-${color}-color, #3b82f6)`,
        borderRadius: '8px',
        boxShadow: isSelected
          ? '0 0 0 2px #3b82f6, 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
          : '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        transition: isDragging ? 'none' : 'box-shadow 0.3s ease, transform 0.2s ease',
        transform: isDragging ? 'scale(1.03)' : isSelected ? 'scale(1.02)' : 'scale(1)',
        zIndex: isDragging ? 100 : (isSelected ? 10 : 1),
        position: 'absolute',
        cursor: 'move',
        backgroundColor: '#ffffff'
      }}
      onClick={handleNodeClick}
    >
      {/* Node header */}
      <div
        className="node-header p-2 flex justify-between items-center rounded-t-md"
        style={{
          backgroundColor: `var(--node-${color}-bg, #eff6ff)`,
          borderBottom: `1px solid var(--node-${color}-border, #dbeafe)`,
          cursor: 'move',
          borderTopLeftRadius: '6px',
          borderTopRightRadius: '6px'
        }}
        onMouseDown={handleMouseDown}
      >
        <div className="flex items-center">
          <div
            className="w-6 h-6 rounded-full flex items-center justify-center mr-2"
            style={{ backgroundColor: `var(--node-${color}-color, #3b82f6)`, opacity: 0.9 }}
          >
            <i className={`fas fa-${icon} text-white text-xs`}></i>
          </div>
          <span className="font-medium text-gray-800 text-sm truncate">{title}</span>
        </div>
        <div className="flex space-x-1">
          <button
            className="text-gray-500 hover:text-blue-500 p-1 rounded-full hover:bg-blue-50 transition-colors text-xs"
            title="Edit Node Configuration"
            onClick={(e) => { e.stopPropagation(); onEdit(); }}
          >
            <i className="fas fa-cog"></i>
          </button>
          <button
            className="text-gray-500 hover:text-red-500 p-1 rounded-full hover:bg-red-50 transition-colors text-xs"
            title="Delete Node"
            onClick={(e) => { e.stopPropagation(); onDelete(); }}
          >
            <i className="fas fa-trash-alt"></i>
          </button>
        </div>
      </div>

      {/* Node content */}
      <div className="p-3 text-sm">
        <div className="mb-2 flex justify-between items-center">
          <span className="text-xs font-medium text-gray-600 uppercase tracking-wider">Config</span>
          <button
            className="text-xs text-blue-500 hover:text-blue-700 flex items-center"
            onClick={(e) => { e.stopPropagation(); onEdit(); }}
          >
            <span>Edit</span>
            <i className="fas fa-edit ml-1 text-xs"></i>
          </button>
        </div>
        <div className="bg-gray-50 rounded-md p-2 border border-gray-100 text-xs">
          {getConfigSummary()}
        </div>
      </div>

      {/* Connection points */}
      <div className="connection-points">
        {/* Input points */}
        <div className="inputs absolute left-0 top-0 bottom-0 w-3">
          {inputPositions.length > 0 ? (
            inputPositions.map(input => (
              <div
                key={input.id || input.name}
                className="input-point"
                data-port={input.id || input.name}
                data-type={input.type}
                title={`Input: ${input.name} (${input.type})`}
                onMouseDown={(e) => handleInputPointMouseDown(e, input.id || input.name)}
                onMouseOver={(e) => handlePortMouseOver(e, 'input', input.name, input.type)}
                onMouseOut={handlePortMouseOut}
                style={{ position: 'absolute', top: `${input.y}px` }}
              >
                <span className="port-label">{input.name}</span>
              </div>
            ))
          ) : (
            // Display a placeholder input point if there are no inputs
            <div
              className="input-point opacity-50"
              style={{ position: 'absolute', top: '50px' }}
              title="No inputs available"
              onMouseDown={(e) => handleInputPointMouseDown(e, 'none')}
              onMouseOver={(e) => handlePortMouseOver(e, 'input', 'none', 'any')}
              onMouseOut={handlePortMouseOut}
            >
              <span className="port-label">No inputs</span>
            </div>
          )}
        </div>

        {/* Output points */}
        <div className="outputs absolute right-0 top-0 bottom-0 w-3">
          {outputPositions.length > 0 ? (
            outputPositions.map(output => (
              <div
                key={output.id || output.name}
                className="output-point"
                data-port={output.id || output.name}
                data-type={output.type}
                title={`Output: ${output.name} (${output.type})`}
                onMouseDown={(e) => handleOutputPointMouseDown(e, output.id || output.name)}
                onMouseOver={(e) => handlePortMouseOver(e, 'output', output.name, output.type)}
                onMouseOut={handlePortMouseOut}
                style={{ position: 'absolute', top: `${output.y}px` }}
              >
                <span className="port-label">{output.name}</span>
              </div>
            ))
          ) : (
            // Display a placeholder output point if there are no outputs
            <div
              className="output-point opacity-50"
              style={{ position: 'absolute', top: '50px' }}
              title="No outputs available"
              onMouseDown={(e) => handleOutputPointMouseDown(e, 'none')}
              onMouseOver={(e) => handlePortMouseOver(e, 'output', 'none', 'any')}
              onMouseOut={handlePortMouseOut}
            >
              <span className="port-label">No outputs</span>
            </div>
          )}
        </div>
      </div>

      {/* Resize handle */}
      <div className="resize-handle"></div>
    </div>
  );
};

export default Node;
