import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useDrop } from 'react-dnd';
import { NodeData, Connection } from '../../types';
import Node from './Node';
import CanvasControls from './CanvasControls';
import Minimap from './Minimap';
import ContextMenu from './ContextMenu';
import NodeSearch from './NodeSearch';
import { useNodeTypes } from '../../contexts/NodeTypesContext';
import './ConnectionWires.css';
import './WorkflowCanvas.css';

interface WorkflowCanvasProps {
  nodes: NodeData[];
  connections: Connection[];
  selectedNode: string | null;
  selectedConnection: string | null;
  zoom: {
    level: number;
    min: number;
    max: number;
    step: number;
  };
  onAddNode: (type: string, x: number, y: number) => string;
  onSelectNode: (nodeId: string | null) => void;
  onDeleteNode: (nodeId: string) => void;
  onAddConnection: (fromNodeId: string, fromPort: string, toNodeId: string, toPort: string) => string | null;
  onDeleteConnection: (connectionId: string) => void;
  onOpenNodeEditor: (nodeId: string) => void;
  onUndo: () => void;
  onRedo: () => void;
  onUpdateNodePosition?: (nodeId: string, x: number, y: number) => void;
  onUpdateNodeConfig?: (nodeId: string, config: Record<string, any>) => void;
}

const WorkflowCanvas: React.FC<WorkflowCanvasProps> = ({
  nodes,
  connections,
  selectedNode,
  selectedConnection,
  zoom,
  onAddNode,
  onSelectNode,
  onDeleteNode,
  onAddConnection,
  onDeleteConnection,
  onOpenNodeEditor,
  onUndo,
  onRedo,
  onUpdateNodePosition,
  onUpdateNodeConfig
}) => {
  // We'll use document.querySelector instead of refs to avoid TypeScript issues
  const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 });
  const [showMinimap, setShowMinimap] = useState(true);
  const [contextMenu, setContextMenu] = useState<{ x: number, y: number } | null>(null);
  const [showSearch, setShowSearch] = useState(false);

  // Get node types from context
  let nodeTypes: Record<string, { id: string, inputs: Array<{id: string, name: string, type: string}>, outputs: Array<{id: string, name: string, type: string}> }> = {};
  let isTypeCompatible = async (sourceType: string, targetType: string): Promise<boolean> => {
    // Default implementation if context is not available
    return sourceType === targetType || sourceType === 'any' || targetType === 'any';
  };

  try {
    const context = useNodeTypes();
    nodeTypes = context.nodeTypes as Record<string, { id: string, inputs: Array<{id: string, name: string, type: string}>, outputs: Array<{id: string, name: string, type: string}> }>;
    isTypeCompatible = context.isTypeCompatible;
  } catch (error) {
    console.warn('NodeTypesContext not available, using fallback values');
  }

  // Get node ports definition
  const getNodePorts = (type: string) => {
    // First try to get from the context
    if (nodeTypes && nodeTypes[type]) {
      return nodeTypes[type];
    }

    // Fallback to hardcoded values if not found in context
    const nodePorts: Record<string, { inputs: Array<{name: string, type: string}>, outputs: Array<{name: string, type: string}> }> = {
      data_loader: {
        inputs: [],
        outputs: [{ name: 'data', type: 'dataset' }]
      },
      data_transform: {
        inputs: [{ name: 'data', type: 'dataset' }],
        outputs: [{ name: 'transformed_data', type: 'dataset' }]
      },
      feature_engineering: {
        inputs: [{ name: 'data', type: 'dataset' }],
        outputs: [{ name: 'features', type: 'features' }]
      },
      train_model: {
        inputs: [{ name: 'features', type: 'features' }, { name: 'labels', type: 'labels' }],
        outputs: [{ name: 'model', type: 'model' }]
      },
      evaluate: {
        inputs: [{ name: 'model', type: 'model' }, { name: 'test_data', type: 'dataset' }],
        outputs: [{ name: 'metrics', type: 'metrics' }]
      },
      predict: {
        inputs: [{ name: 'model', type: 'model' }, { name: 'data', type: 'dataset' }],
        outputs: [{ name: 'predictions', type: 'predictions' }]
      },
      deploy_model: {
        inputs: [{ name: 'model', type: 'model' }],
        outputs: [{ name: 'service', type: 'service' }]
      },
      monitoring: {
        inputs: [{ name: 'service', type: 'service' }, { name: 'predictions', type: 'predictions' }],
        outputs: []
      }
    };

    return nodePorts[type] || { inputs: [], outputs: [] };
  };
  const [tempConnection, setTempConnection] = useState<{
    fromNodeId: string;
    fromPort: string;
    fromEl: HTMLElement;
    mouseX: number;
    mouseY: number;
    fromType?: string;
  } | null>(null);
  const [zoomLevel, setZoomLevel] = useState(zoom.level);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [lastMousePos, setLastMousePos] = useState({ x: 0, y: 0 });

  // Set up drop target for components
  const [{ isOver }, drop] = useDrop({
    accept: 'component',
    drop: (item: { type: string }, monitor) => {
      const offset = monitor.getClientOffset();
      const canvas = document.querySelector('.workflow-canvas');
      if (offset && canvas) {
        const canvasRect = canvas.getBoundingClientRect();
        const x = (offset.x - canvasRect.left - panOffset.x) / zoomLevel;
        const y = (offset.y - canvasRect.top - panOffset.y) / zoomLevel;
        onAddNode(item.type, x, y);
      }
      return undefined;
    },
    collect: (monitor) => ({
      isOver: !!monitor.isOver(),
    }),
  });

  // Update canvas size on resize
  useEffect(() => {
    const updateCanvasSize = () => {
      const canvas = document.querySelector('.workflow-canvas');
      if (canvas) {
        setCanvasSize({
          width: canvas.clientWidth,
          height: canvas.clientHeight
        });
      }
    };

    updateCanvasSize();
    window.addEventListener('resize', updateCanvasSize);
    return () => window.removeEventListener('resize', updateCanvasSize);
  }, []);

  // Center view on all nodes or reset to center if no nodes
  const centerView = useCallback(() => {
    if (nodes.length === 0) {
      // If no nodes, just reset to center
      setZoomLevel(1);
      setPanOffset({ x: 0, y: 0 });
      return;
    }

    // Calculate bounding box of all nodes
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;

    nodes.forEach(node => {
      // Use node width/height or default values
      const nodeWidth = node.width || 240;
      const nodeHeight = node.height || 120;

      minX = Math.min(minX, node.x);
      minY = Math.min(minY, node.y);
      maxX = Math.max(maxX, node.x + nodeWidth);
      maxY = Math.max(maxY, node.y + nodeHeight);
    });

    // Get canvas dimensions
    const canvas = document.querySelector('.workflow-canvas');
    if (!canvas) return;

    const canvasWidth = canvas.clientWidth;
    const canvasHeight = canvas.clientHeight;

    // Calculate center of nodes
    const nodesCenterX = (minX + maxX) / 2;
    const nodesCenterY = (minY + maxY) / 2;

    // Calculate required zoom level to fit all nodes with padding
    const nodesWidth = maxX - minX;
    const nodesHeight = maxY - minY;
    const padding = 100; // Padding around nodes

    const zoomX = canvasWidth / (nodesWidth + padding * 2);
    const zoomY = canvasHeight / (nodesHeight + padding * 2);
    const newZoomLevel = Math.min(Math.min(zoomX, zoomY), 1); // Cap at 1.0 to avoid zooming in too much

    // Calculate pan offset to center nodes
    const panX = (canvasWidth / 2) - (nodesCenterX * newZoomLevel);
    const panY = (canvasHeight / 2) - (nodesCenterY * newZoomLevel);

    // Apply new zoom and pan with animation
    setZoomLevel(newZoomLevel);
    setPanOffset({ x: panX, y: panY });

    // Show a visual indicator that centering has occurred
    const indicator = document.createElement('div');
    indicator.className = 'center-view-indicator';
    indicator.innerHTML = '<i class="fas fa-crosshairs mr-2"></i> View Centered';
    indicator.style.position = 'absolute';
    indicator.style.top = '50%';
    indicator.style.left = '50%';
    indicator.style.transform = 'translate(-50%, -50%)';
    indicator.style.backgroundColor = 'rgba(59, 130, 246, 0.9)';
    indicator.style.color = 'white';
    indicator.style.padding = '10px 20px';
    indicator.style.borderRadius = '8px';
    indicator.style.zIndex = '1000';
    indicator.style.fontWeight = 'bold';
    indicator.style.fontSize = '14px';

    canvas.appendChild(indicator);

    // Remove after animation completes
    setTimeout(() => {
      indicator.style.opacity = '0';
      indicator.style.transition = 'opacity 0.3s ease';
      setTimeout(() => {
        if (canvas.contains(indicator)) {
          canvas.removeChild(indicator);
        }
      }, 300);
    }, 1500);
  }, [nodes, zoomLevel]);

  // Toggle minimap with keyboard shortcut and handle other global shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Toggle minimap with Alt+M
      if (e.key === 'm' && e.altKey) {
        setShowMinimap(prev => !prev);
      }

      // Center view with 'c' key
      if (e.key === 'c' && !e.ctrlKey && !e.altKey) {
        centerView();
      }

      // Open search with Ctrl+F or Cmd+F
      if ((e.key === 'f' && (e.ctrlKey || e.metaKey)) && !e.shiftKey) {
        e.preventDefault(); // Prevent browser's find dialog
        setShowSearch(true);
      }

      // Open search with / (slash) when no input is focused
      if (e.key === '/' && document.activeElement === document.body) {
        e.preventDefault();
        setShowSearch(true);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [centerView]); // Add centerView to the dependency array

  // Handle wheel event for zooming
  useEffect(() => {
    // Create a memoized wheel handler to avoid dependency issues
    const handleWheel = (e: WheelEvent) => {
      // Prevent default scrolling behavior
      e.preventDefault();

      // Get mouse position relative to canvas for zoom targeting
      const canvas = document.querySelector('.workflow-canvas');
      if (!canvas) return;

      const rect = canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      // Calculate zoom direction and new zoom level
      const zoomDirection = e.deltaY < 0 ? 1 : -1;
      const zoomFactor = 0.1; // How much to zoom per scroll
      const newZoomLevel = Math.max(
        zoom.min,
        Math.min(zoom.max, zoomLevel + zoomDirection * zoomFactor)
      );

      // Calculate new pan offset to zoom toward/away from mouse position
      if (newZoomLevel !== zoomLevel) {
        const zoomRatio = newZoomLevel / zoomLevel;

        // Adjust pan offset to keep mouse position fixed during zoom
        const newPanOffsetX = mouseX - (mouseX - panOffset.x) * zoomRatio;
        const newPanOffsetY = mouseY - (mouseY - panOffset.y) * zoomRatio;

        setZoomLevel(newZoomLevel);
        setPanOffset({ x: newPanOffsetX, y: newPanOffsetY });
      }
    };

    // Use a type assertion to fix the TypeScript error
    const canvas = document.querySelector('.workflow-canvas') as HTMLElement;
    if (canvas) {
      // Use a type-safe event listener
      const wheelListener = (e: Event) => {
        handleWheel(e as WheelEvent);
      };

      canvas.addEventListener('wheel', wheelListener, { passive: false });

      return () => {
        canvas.removeEventListener('wheel', wheelListener);
      };
    }

    return undefined;
  }, [zoomLevel, panOffset, zoom.min, zoom.max]);

  // Handle zoom
  const handleZoomIn = () => {
    if (zoomLevel < zoom.max) {
      setZoomLevel((prev: number) => Math.min(prev + zoom.step, zoom.max));
    }
  };

  const handleZoomOut = () => {
    if (zoomLevel > zoom.min) {
      setZoomLevel((prev: number) => Math.max(prev - zoom.step, zoom.min));
    }
  };

  const handleZoomReset = () => {
    setZoomLevel(1);
    setPanOffset({ x: 0, y: 0 });
  };



  // Update zoom level class when zoom changes
  useEffect(() => {
    const canvas = document.querySelector('.workflow-canvas');
    if (canvas) {
      // Remove all zoom level classes
      const zoomClasses = Array.from(canvas.classList).filter(cls => cls.startsWith('zoom-level-'));
      zoomClasses.forEach(cls => canvas.classList.remove(cls));

      // Add current zoom level class
      canvas.classList.add(`zoom-level-${zoomLevel.toString().replace('.', '-')}`);
    }
  }, [zoomLevel]);

  // Handle panning with improved performance
  const handleMouseDown = (e: React.MouseEvent) => {
    // Check if we're clicking directly on the canvas (not on a node)
    const isClickingCanvas = e.target === e.currentTarget;

    // Allow panning with:
    // 1. Middle mouse button (button 1) anywhere
    // 2. Alt+Left click anywhere
    // 3. Left click directly on the canvas background (not on nodes)
    if (e.button === 1 || (e.button === 0 && e.altKey) || (e.button === 0 && isClickingCanvas)) {
      setIsPanning(true);
      setLastMousePos({ x: e.clientX, y: e.clientY });
      // Add panning class to canvas
      const canvas = document.querySelector('.workflow-canvas') as HTMLElement;
      if (canvas) {
        canvas.classList.add('panning');
      }
      e.preventDefault();
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    // Smooth panning with requestAnimationFrame for better performance
    if (isPanning) {
      const dx = e.clientX - lastMousePos.x;
      const dy = e.clientY - lastMousePos.y;

      // Use requestAnimationFrame for smoother updates
      requestAnimationFrame(() => {
        setPanOffset(prev => ({ x: prev.x + dx, y: prev.y + dy }));
      });

      setLastMousePos({ x: e.clientX, y: e.clientY });
    }

    // Update temp connection if drawing
    if (tempConnection) {
      // Use requestAnimationFrame for smoother updates
      requestAnimationFrame(() => {
        setTempConnection({
          ...tempConnection,
          mouseX: e.clientX,
          mouseY: e.clientY
        });
      });
    }
  };

  const handleMouseUp = () => {
    if (isPanning) {
      setIsPanning(false);
      // Remove panning class
      const canvas = document.querySelector('.workflow-canvas') as HTMLElement;
      if (canvas) {
        canvas.classList.remove('panning');
      }
    }
  };

  // Handle canvas click
  const handleCanvasClick = (e: React.MouseEvent) => {
    // Only deselect if clicking directly on the canvas (not on a node)
    const canvas = document.querySelector('.workflow-canvas');
    if (e.target === canvas) {
      onSelectNode(null);

      // Close context menu on left click
      if (e.button === 0) {
        setContextMenu(null);
      }
    }

    // Cancel temp connection if drawing
    if (tempConnection) {
      setTempConnection(null);
      // Remove the connecting class
      document.body.classList.remove('connecting');
    }
  };

  // Handle right click for context menu
  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    // Only show context menu when right-clicking directly on the canvas
    if (e.target === e.currentTarget) {
      // Calculate position relative to the canvas
      const rect = e.currentTarget.getBoundingClientRect();
      const x = (e.clientX - rect.left - panOffset.x) / zoomLevel;
      const y = (e.clientY - rect.top - panOffset.y) / zoomLevel;
      setContextMenu({ x, y });
    } else {
      setContextMenu(null);
    }
  };

  // Start drawing a connection
  const handleStartConnection = (nodeId: string, port: string, el: HTMLElement) => {
    // Get the port type for visual styling
    const fromNode = nodes.find((n: NodeData) => n.id === nodeId);
    if (fromNode) {
      const fromPorts = getNodePorts(fromNode.type);
      const fromPort = fromPorts.outputs.find((p: any) =>
        (p.id && p.id === port) || p.name === port
      );
      const fromType = fromPort?.type || 'any';

      console.log(`Starting connection from node ${nodeId}, port ${port}, type ${fromType}`);

      // Store the port type with the connection
      setTempConnection({
        fromNodeId: nodeId,
        fromPort: port,
        fromEl: el,
        mouseX: 0,
        mouseY: 0,
        fromType: fromType
      });

      // Add a class to the body to indicate we're connecting
      document.body.classList.add('connecting');

      // Add event listener for mouse movement to update the temp connection
      const handleMouseMove = (e: MouseEvent) => {
        setTempConnection(prev => {
          if (!prev) return null;
          return {
            ...prev,
            mouseX: e.clientX,
            mouseY: e.clientY
          };
        });
      };

      document.addEventListener('mousemove', handleMouseMove);

      // Remove the event listener when the connection is complete or cancelled
      const cleanup = () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', cleanup);
      };

      document.addEventListener('mouseup', cleanup);
    }
  };

  // Finish drawing a connection
  const handleEndConnection = async (nodeId: string, port: string) => {
    // Don't remove the connecting class yet - we'll do that after validation

    if (tempConnection && tempConnection.fromNodeId !== nodeId) {
      console.log(`Ending connection to node ${nodeId}, port ${port}`);

      // Check type compatibility
      const fromNode = nodes.find((n: NodeData) => n.id === tempConnection.fromNodeId);
      const toNode = nodes.find((n: NodeData) => n.id === nodeId);

      if (fromNode && toNode) {
        // Get port types
        const fromPorts = getNodePorts(fromNode.type);
        const toPorts = getNodePorts(toNode.type);

        console.log(`From node type: ${fromNode.type}, To node type: ${toNode.type}`);
        console.log(`From ports:`, fromPorts.outputs);
        console.log(`To ports:`, toPorts.inputs);

        const fromPort = fromPorts.outputs.find((p: any) =>
          (p.id && p.id === tempConnection.fromPort) || p.name === tempConnection.fromPort
        );
        const toPort = toPorts.inputs.find((p: any) =>
          (p.id && p.id === port) || p.name === port
        );

        console.log(`Selected from port:`, fromPort);
        console.log(`Selected to port:`, toPort);

        if (!fromPort) {
          console.warn(`Output port ${tempConnection.fromPort} not found on node ${fromNode.id} (${fromNode.type})`);
          setTempConnection(null);
          document.body.classList.remove('connecting');
          return;
        }

        if (!toPort) {
          console.warn(`Input port ${port} not found on node ${toNode.id} (${toNode.type})`);
          setTempConnection(null);
          document.body.classList.remove('connecting');
          return;
        }

        const fromType = fromPort?.type || 'any';
        const toType = toPort?.type || 'any';

        console.log(`Checking compatibility: ${fromType} -> ${toType}`);

        // Create a temporary connection indicator to show validation state
        const connectionIndicator = document.createElement('div');
        connectionIndicator.className = 'connection-type-indicator validating';
        connectionIndicator.textContent = 'Validating connection...';
        connectionIndicator.style.position = 'absolute';
        connectionIndicator.style.left = `${(fromNode.x + toNode.x) / 2}px`;
        connectionIndicator.style.top = `${(fromNode.y + toNode.y) / 2}px`;
        document.body.appendChild(connectionIndicator);

        try {
          // Simple type compatibility check - same types or 'any' type should always be compatible
          let compatible = false;

          // First do a simple check for exact match or 'any' type
          if (fromType === toType || fromType === 'any' || toType === 'any') {
            compatible = true;
          } else {
            // If not an exact match, check with the backend
            try {
              compatible = await isTypeCompatible(fromType, toType);
            } catch (error) {
              console.error('Error checking type compatibility with backend:', error);
              // Fallback to simple compatibility check if backend fails
              compatible = fromType === toType || fromType === 'any' || toType === 'any';
            }
          }

          if (!compatible) {
            console.warn(`Incompatible types: ${fromType} -> ${toType}`);

            // Show incompatible indicator
            connectionIndicator.textContent = `Incompatible types: ${fromType} → ${toType}`;
            connectionIndicator.className = 'connection-type-indicator invalid';
            connectionIndicator.style.backgroundColor = '#fee2e2';
            connectionIndicator.style.color = '#ef4444';

            // Remove indicator after 3 seconds
            setTimeout(() => {
              document.body.removeChild(connectionIndicator);
            }, 3000);

            // Don't create the connection if types are incompatible
            setTempConnection(null);
            document.body.classList.remove('connecting');
            return;
          } else {
            // Show compatible indicator
            connectionIndicator.textContent = `Connected: ${fromType} → ${toType}`;
            connectionIndicator.className = 'connection-type-indicator valid';
            connectionIndicator.style.backgroundColor = '#dcfce7';
            connectionIndicator.style.color = '#16a34a';

            // Remove indicator after 2 seconds
            setTimeout(() => {
              document.body.removeChild(connectionIndicator);
            }, 2000);

            // Types are compatible, add the connection
            console.log(`Creating connection from ${tempConnection.fromNodeId}.${tempConnection.fromPort} to ${nodeId}.${port}`);
            onAddConnection(tempConnection.fromNodeId, tempConnection.fromPort, nodeId, port);
            document.body.classList.remove('connecting');
          }
        } catch (error) {
          console.error('Error in connection validation process:', error);

          // Show error indicator
          connectionIndicator.textContent = `Error validating connection`;
          connectionIndicator.className = 'connection-type-indicator';
          connectionIndicator.style.backgroundColor = '#fef3c7';
          connectionIndicator.style.color = '#d97706';

          // Remove indicator after 3 seconds
          setTimeout(() => {
            document.body.removeChild(connectionIndicator);
          }, 3000);

          // Allow connection despite error for development purposes
          console.log('Allowing connection despite error for development purposes');
          onAddConnection(tempConnection.fromNodeId, tempConnection.fromPort, nodeId, port);
          document.body.classList.remove('connecting');
        }
      } else {
        // If nodes not found, don't create connection
        console.warn('Source or target node not found');
        document.body.classList.remove('connecting');
      }
    } else {
      document.body.classList.remove('connecting');
      setTempConnection(null);
    }
  };

  // Render connections
  const renderConnections = () => {
    return connections.map((conn: Connection) => {
      // Find the DOM elements for the connection points
      const fromNode = nodes.find((n: NodeData) => n.id === conn.from.nodeId);
      const toNode = nodes.find((n: NodeData) => n.id === conn.to.nodeId);

      if (!fromNode || !toNode) return null;

      // Get the port types

      // Find the port types
      const fromPorts = getNodePorts(fromNode.type);
      const toPorts = getNodePorts(toNode.type);

      // Look for port by id or name
      const fromPort = fromPorts.outputs.find((p: any) =>
        (p.id && p.id === conn.from.port) || p.name === conn.from.port
      );
      const toPort = toPorts.inputs.find((p: any) =>
        (p.id && p.id === conn.to.port) || p.name === conn.to.port
      );

      const fromType = fromPort?.type || 'any';
      const toType = toPort?.type || 'any';

      // Calculate port positions
      const getPortPosition = (node: NodeData, portName: string, isInput: boolean) => {
        const nodeType = node.type;
        const ports = getNodePorts(nodeType);
        const portList = isInput ? ports.inputs : ports.outputs;

        // Find the port index by id or name
        const portIndex = portList.findIndex((p: any) =>
          (p.id && p.id === portName) || p.name === portName
        );

        // If port not found, use a default position in the middle of the node
        if (portIndex === -1) {
          console.warn(`Port ${portName} not found on node ${node.id} of type ${node.type}`);
          return {
            x: isInput ? node.x : node.x + (node.width || 240),
            y: node.y + (node.height || 100) / 2
          };
        }

        // Calculate position based on index
        const nodeHeight = node.height || 100; // Use node height or default
        const spacing = nodeHeight / (portList.length + 1);
        const y = node.y + spacing * (portIndex + 1);

        return {
          x: isInput ? node.x : node.x + (node.width || 240), // Left or right side, directly at the node edge
          y
        };
      };

      // Get port positions
      const fromPos = getPortPosition(fromNode, conn.from.port, false);
      const toPos = getPortPosition(toNode, conn.to.port, true);

      // Calculate connection path
      const fromX = fromPos.x * zoomLevel;
      const fromY = fromPos.y * zoomLevel;
      const toX = toPos.x * zoomLevel;
      const toY = toPos.y * zoomLevel;

      // Create SVG path with a more natural curve
      const dx = Math.abs(toX - fromX);
      const controlPointDistance = Math.max(50, dx * 0.4); // Adjust control point distance based on horizontal distance
      const path = `M ${fromX} ${fromY} C ${fromX + controlPointDistance} ${fromY}, ${toX - controlPointDistance} ${toY}, ${toX} ${toY}`;

      // Determine connection color based on type
      const getConnectionClass = (type: string) => {
        const typeClasses: Record<string, string> = {
          'dataset': 'connection-dataset',
          'features': 'connection-features',
          'model': 'connection-model',
          'metrics': 'connection-metrics',
          'predictions': 'connection-predictions',
          'service': 'connection-service',
          'labels': 'connection-labels'
        };

        return typeClasses[type] || '';
      };

      const connectionClass = getConnectionClass(fromType);

      return (
        <svg
          key={conn.id}
          className="absolute top-0 left-0 w-full h-full pointer-events-none"
          style={{
            transform: `translate(${panOffset.x}px, ${panOffset.y}px)`,
            willChange: 'transform',
            transition: isPanning ? 'none' : 'transform 0.1s ease-out'
          }}
        >
          <path
            d={path}
            className={`connection-path ${connectionClass} ${conn.id === selectedConnection ? 'selected' : ''}`}
            onClick={() => onDeleteConnection(conn.id)}
            data-from-type={fromType}
            data-to-type={toType}
          />

          {/* Add a small label showing the connection type */}
          <text
            x={(fromX + toX) / 2}
            y={(fromY + toY) / 2 - 10 * zoomLevel}
            className="connection-label"
            textAnchor="middle"
            fill="#666"
            fontSize={`${10 * Math.max(0.8, Math.min(1.2, zoomLevel))}`}
          >
            {fromType}
          </text>
        </svg>
      );
    });
  };

  // Render temporary connection while drawing
  const renderTempConnection = () => {
    if (!tempConnection) return null;

    const canvas = document.querySelector('.workflow-canvas');
    if (!canvas) return null;

    // Get the source node and port type for styling
    const sourceNode = nodes.find((n: NodeData) => n.id === tempConnection.fromNodeId);
    const sourceType = tempConnection.fromType || 'any';

    const fromNode = nodes.find((n: NodeData) => n.id === tempConnection.fromNodeId);
    if (!fromNode) return null;

    const canvasRect = canvas.getBoundingClientRect();
    // Calculate port position
    const getPortPosition = (node: NodeData, portName: string, isInput: boolean) => {
      const nodeType = node.type;
      const ports = getNodePorts(nodeType);
      const portList = isInput ? ports.inputs : ports.outputs;

      // Find the port index by id or name
      const portIndex = portList.findIndex((p: any) =>
        (p.id && p.id === portName) || p.name === portName
      );

      // If port not found, use a default position in the middle of the node
      if (portIndex === -1) {
        console.warn(`Port ${portName} not found on node ${node.id} of type ${node.type}`);
        return {
          x: isInput ? node.x : node.x + (node.width || 240),
          y: node.y + (node.height || 100) / 2
        };
      }

      // Calculate position based on index
      const nodeHeight = node.height || 100; // Use node height or default
      const spacing = nodeHeight / (portList.length + 1);
      const y = node.y + spacing * (portIndex + 1);

      return {
        x: isInput ? node.x : node.x + (node.width || 240), // Left or right side, directly at the node edge
        y
      };
    };

    const fromPos = getPortPosition(fromNode, tempConnection.fromPort, false);
    const fromX = fromPos.x * zoomLevel;
    const fromY = fromPos.y * zoomLevel;

    // Calculate mouse position relative to canvas
    // If mouseX/Y are 0, use a default offset
    const toX = tempConnection.mouseX
      ? (tempConnection.mouseX - canvasRect.left - panOffset.x)
      : fromX + 100 * zoomLevel; // Default offset if no mouse position

    const toY = tempConnection.mouseY
      ? (tempConnection.mouseY - canvasRect.top - panOffset.y)
      : fromY; // Default to same height if no mouse position

    // Create SVG path with a more natural curve
    const dx = Math.abs(toX - fromX);
    const controlPointDistance = Math.max(50 * zoomLevel, dx * 0.4); // Adjust control point distance based on horizontal distance
    const path = `M ${fromX} ${fromY} C ${fromX + controlPointDistance} ${fromY}, ${toX - controlPointDistance} ${toY}, ${toX} ${toY}`;

    // Determine connection color based on type
    const getConnectionColor = (type: string) => {
      const typeColors: Record<string, string> = {
        'string': '#60a5fa',
        'number': '#a78bfa',
        'boolean': '#f87171',
        'object': '#4ade80',
        'array': '#fbbf24',
        'any': '#9ca3af',
        'trigger': '#ec4899',
        'dataset': '#0ea5e9',
        'model': '#8b5cf6',
        'features': '#10b981',
        'predictions': '#f59e0b'
      };

      return typeColors[type] || '#3b82f6';
    };

    const connectionColor = getConnectionColor(tempConnection.fromType || 'any');

    // Check if mouse is over a valid target
    const elementsUnderMouse = document.elementsFromPoint(tempConnection.mouseX, tempConnection.mouseY);
    const targetElement = elementsUnderMouse.find(el => el.classList.contains('input-point'));
    let isOverValidTarget = !!targetElement;
    let isCompatible = true;

    // If over a target, check type compatibility
    if (isOverValidTarget && targetElement) {
      const targetType = targetElement.getAttribute('data-type') || 'any';
      const sourceType = tempConnection.fromType || 'any';

      // Simple compatibility check (will be replaced by backend validation)
      isCompatible = sourceType === targetType || sourceType === 'any' || targetType === 'any';
    }

    return (
      <>
        <svg
          className="absolute top-0 left-0 w-full h-full pointer-events-none"
          style={{
            transform: `translate(${panOffset.x}px, ${panOffset.y}px)`,
            willChange: 'transform',
            transition: isPanning ? 'none' : 'transform 0.1s ease-out'
          }}
        >
          <path
            d={path}
            className={`connection-path ${isOverValidTarget ? (isCompatible ? 'valid' : 'invalid') : ''}`}
            strokeDasharray="5,5"
            stroke={connectionColor}
            strokeWidth="3"
            data-from-type={tempConnection?.fromType || 'any'}
          />

          {/* Add a small label showing the connection type */}
          <text
            x={(fromX + toX) / 2}
            y={(fromY + toY) / 2 - 10 * zoomLevel}
            className="connection-label"
            textAnchor="middle"
            fill={connectionColor}
            fontSize={`${12 * Math.max(0.8, Math.min(1.2, zoomLevel))}`}
            fontWeight="bold"
          >
            {tempConnection?.fromType || 'any'}
          </text>

          {/* Add a circle at the end of the temp connection */}
          <circle
            cx={toX}
            cy={toY}
            r={`${8 * Math.max(0.8, Math.min(1.2, zoomLevel))}`}
            fill={connectionColor}
            opacity="0.7"
          />
        </svg>

        {/* Type indicator that follows the mouse */}
        <div
          className="connection-type-indicator"
          data-type={tempConnection?.fromType || 'any'}
          style={{
            position: 'fixed',
            left: tempConnection?.mouseX ? tempConnection.mouseX + 15 : 0,
            top: tempConnection?.mouseY ? tempConnection.mouseY + 15 : 0,
            pointerEvents: 'none',
            zIndex: 1000
          }}
        >
          {tempConnection?.fromType || 'any'}
          {isOverValidTarget && (
            <span className={isCompatible ? 'text-green-600' : 'text-red-600'}>
              {isCompatible ? ' ✓' : ' ✗'}
            </span>
          )}
        </div>
      </>
    );
  };

  return (
    <div
      className="relative flex-grow"
      style={{ height: 'calc(100vh - 140px)', minHeight: '800px' }}
    >
      <div
        ref={drop}
        className={`workflow-canvas p-4 w-full h-full relative overflow-hidden ${isOver ? 'bg-blue-50' : ''} zoom-level-${zoomLevel.toString().replace('.', '-')}`}
        onClick={handleCanvasClick}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onContextMenu={handleContextMenu}
      >
        {/* Canvas content container with zoom and pan */}
        <div
          className="absolute top-0 left-0 w-full h-full"
          style={{
            transform: `scale(${zoomLevel}) translate(${panOffset.x / zoomLevel}px, ${panOffset.y / zoomLevel}px)`,
            transformOrigin: '0 0',
            willChange: 'transform', // Hint to browser to optimize transform performance
            transition: isPanning ? 'none' : 'transform 0.3s cubic-bezier(0.215, 0.61, 0.355, 1)', // Smooth transition with easing
            pointerEvents: 'none' // Allow clicking through to the canvas
          }}
        >
          {/* Render nodes */}
          {nodes.map((node: NodeData) => (
            <Node
              key={node.id}
              node={node}
              isSelected={node.id === selectedNode}
              onSelect={() => onSelectNode(node.id)}
              onDelete={() => onDeleteNode(node.id)}
              onEdit={() => onOpenNodeEditor(node.id)}
              onStartConnection={handleStartConnection}
              onEndConnection={handleEndConnection}
              onUpdatePosition={onUpdateNodePosition}
              onUpdateConfig={onUpdateNodeConfig}
            />
          ))}
        </div>

        {/* Render connections */}
        {renderConnections()}
        {renderTempConnection()}

        {/* Placeholder when empty */}
        {nodes.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center text-gray-400">
            <div className="text-center">
              <i className="fas fa-project-diagram text-5xl mb-2"></i>
              <p>Drag components here to build your workflow</p>
            </div>
          </div>
        )}

        {/* Canvas controls */}
        <CanvasControls
          onZoomIn={handleZoomIn}
          onZoomOut={handleZoomOut}
          onZoomReset={handleZoomReset}
          onCenterView={centerView}
          onSearch={() => setShowSearch(true)}
          onUndo={onUndo}
          onRedo={onRedo}
          zoomLevel={zoomLevel}
        />

        {/* Minimap toggle button - only shown when minimap is hidden */}
        {!showMinimap && (
          <button
            className="absolute bottom-4 left-4 bg-white bg-opacity-90 rounded-lg shadow-md p-2 text-gray-600 hover:text-blue-600 z-50"
            onClick={() => setShowMinimap(true)}
            title="Show Minimap (Alt+M)"
          >
            <i className="fas fa-map text-lg"></i>
          </button>
        )}

        {/* Keyboard shortcut hints */}
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-white bg-opacity-80 text-gray-700 text-xs py-1 px-3 rounded-full shadow-sm transition-opacity duration-300 hover:opacity-100 opacity-70">
          <span className="mr-3"><kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs font-mono">Scroll</kbd> to zoom in/out</span>
          <span className="mr-3"><kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs font-mono">Alt+Click</kbd> or <kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs font-mono">Middle-Click</kbd> to pan</span>
          <span className="mr-3"><kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs font-mono">C</kbd> to center view</span>
          <span className="mr-3"><kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs font-mono">Ctrl+F</kbd> or <kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs font-mono">/</kbd> to search</span>
          <span className="mr-3"><kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs font-mono">Alt+M</kbd> toggle minimap</span>
          <span className="mr-3"><kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs font-mono">Right-Click</kbd> for quick actions</span>
          <span><kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs font-mono">?</kbd> for all shortcuts</span>
        </div>

        {/* Context Menu */}
        {contextMenu && (
          <ContextMenu
            x={contextMenu.x}
            y={contextMenu.y}
            onClose={() => setContextMenu(null)}
            onAddNode={onAddNode}
            onPaste={() => console.log('Paste')}
            onSelectAll={() => console.log('Select All')}
            onClearCanvas={() => {
              if (window.confirm('Are you sure you want to clear the canvas? This will remove all nodes and connections.')) {
                nodes.forEach(node => onDeleteNode(node.id));
              }
              setContextMenu(null);
            }}
            onShowShortcuts={() => console.log('Show Shortcuts')}
            onCenterView={centerView}
            onSearch={() => setShowSearch(true)}
          />
        )}

        {/* Search dialog */}
        {showSearch && (
          <NodeSearch
            nodes={nodes}
            onSelectNode={(nodeId) => {
              onSelectNode(nodeId);
              // Find the node and center the view on it
              const node = nodes.find(n => n.id === nodeId);
              if (node) {
                const canvas = document.querySelector('.workflow-canvas');
                if (canvas) {
                  const canvasWidth = canvas.clientWidth;
                  const canvasHeight = canvas.clientHeight;
                  const nodeWidth = node.width || 240;
                  const nodeHeight = node.height || 120;

                  // Calculate center position of the node
                  const nodeCenterX = node.x + nodeWidth / 2;
                  const nodeCenterY = node.y + nodeHeight / 2;

                  // Calculate pan offset to center the node
                  const panX = (canvasWidth / 2) - (nodeCenterX * zoomLevel);
                  const panY = (canvasHeight / 2) - (nodeCenterY * zoomLevel);

                  // Apply pan with animation
                  setPanOffset({ x: panX, y: panY });
                }
              }
            }}
            onClose={() => setShowSearch(false)}
          />
        )}

        {/* Minimap - Toggleable with Alt+M */}
        {showMinimap && (
          <div className="absolute bottom-4 left-4 w-48 h-36 bg-white bg-opacity-90 rounded-lg shadow-lg overflow-hidden border border-gray-200 z-50">
            <div className="absolute top-1 right-1 z-10">
              <button
                className="text-gray-500 hover:text-gray-700 bg-white bg-opacity-80 rounded-full w-5 h-5 flex items-center justify-center text-xs"
                onClick={() => setShowMinimap(false)}
                title="Hide Minimap (Alt+M)"
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            <Minimap
              nodes={nodes}
              canvasSize={canvasSize}
              zoomLevel={zoomLevel}
              panOffset={panOffset}
              onPanChange={setPanOffset}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkflowCanvas;
