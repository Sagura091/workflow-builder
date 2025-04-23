import React, { useState, useEffect, useRef } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { NodeData, Connection, Plugin, WorkflowState, Workflow } from '../../types';
import { getPlugins } from '../../services/api';
import WorkflowHeader from './WorkflowHeader';
import ComponentSidebar from './ComponentSidebar';
import NodeLibrary from './NodeLibrary';
import WorkflowCanvas from './WorkflowCanvas';
import ExecutionPanel from './ExecutionPanel';
import NodeEditorModal from './NodeEditorModal';
import PropertiesPanel from './PropertiesPanel';
import ExecutionVisualization from './ExecutionVisualization';
import KeyboardShortcutsModal from './KeyboardShortcutsModal';
import { useNodeDiscovery } from '../../contexts/NodeDiscoveryContext';
import { WebSocketProvider } from '../../contexts/WebSocketContext';
import { useKeyboardShortcuts, getDefaultShortcuts, Shortcut } from '../../services/keyboardShortcuts';
import { FEATURES } from '../../config';
import { MockAuthProvider } from './MockAuthProvider';
import { useDemoMode } from '../../contexts/DemoModeContext';
import { DemoModeToggle, DemoWelcomeModal, DemoExecutionPanel, DemoFeedbackButton } from '../DemoMode';
import { saveWorkflow, getSavedWorkflows, loadWorkflow, exportWorkflow, createWorkflowSelectionDialog } from './WorkflowOperations';

// Initial state
const initialState: WorkflowState = {
  nodes: [],
  connections: [],
  currentNodeId: 0,
  selectedNode: null,
  selectedConnection: null,
  draggedNode: null,
  isExecuting: false,
  lines: [],
  currentWorkflow: {
    id: null,
    name: "Untitled Workflow",
    nodes: [],
    connections: []
  },
  tempConnection: null,
  zoom: {
    level: 1,
    min: 0.5,
    max: 2,
    step: 0.1
  },
  history: {
    past: [],
    future: []
  },
  connectionStyle: 'fluid',
  validationErrors: []
};

const WorkflowBuilder: React.FC = () => {
  // Get demo mode context with fallback values
  const [showDemoExecutionPanel, setShowDemoExecutionPanel] = useState(false);

  // Use a ref to track if we're in a DemoModeProvider
  const hasDemoProvider = useRef<boolean>(true);

  // Create a dummy context that matches the shape of DemoModeContext
  const dummyDemoContext = {
    isDemoMode: false,
    demoNodes: [],
    demoConnections: [],
    demoPlugins: [],
    updateDemoNodes: (nodes: any[]) => {},
    updateDemoConnections: (connections: any[]) => {},
    executeDemoWorkflow: async () => ({}),
    isExecuting: false,
    executionResults: null,
    toggleDemoMode: () => {},
    resetDemo: () => {}
  };

  // Always call hooks unconditionally at the top level
  // Use a custom hook that doesn't throw
  const useSafeDemoMode = () => {
    try {
      // Try to use the real hook
      return useDemoMode();
    } catch (error) {
      // If it fails, return our dummy context
      console.warn('DemoModeProvider not available, using fallback values');
      return dummyDemoContext;
    }
  };

  // Call our safe hook
  const demoContext = useSafeDemoMode();

  // Update the ref based on whether we got real context
  hasDemoProvider.current = demoContext !== dummyDemoContext;

  // Use the context values, which will be either real or dummy
  const {
    isDemoMode,
    demoNodes,
    demoConnections,
    demoPlugins,
    updateDemoNodes,
    updateDemoConnections,
    executeDemoWorkflow,
    isExecuting: isDemoExecuting,
    executionResults: demoExecutionResults
  } = demoContext;

  // Get node discovery context with fallback
  let nodes = new Map<string, any>();
  let nodesByCategory: Record<string, any[]> = {};
  let nodesLoading = false;
  let nodesError: string | null = null;
  let refreshNodes = async (): Promise<boolean> => { return true; };

  try {
    const nodeDiscovery = useNodeDiscovery();
    nodes = nodeDiscovery.nodes;
    nodesByCategory = nodeDiscovery.nodesByCategory;
    nodesLoading = nodeDiscovery.loading;
    nodesError = nodeDiscovery.error;
    refreshNodes = nodeDiscovery.refreshNodes;
  } catch (error) {
    console.warn('NodeDiscoveryProvider not available, using fallback values');
  }

  // State
  const [state, setState] = useState<WorkflowState>(initialState);
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [showNodeEditor, setShowNodeEditor] = useState<boolean>(false);
  const [showExecutionPanel, setShowExecutionPanel] = useState<boolean>(false);
  const [showNodeLibrary, setShowNodeLibrary] = useState<boolean>(true);
  const [showPropertiesPanel, setShowPropertiesPanel] = useState<boolean>(true);
  const [nodeLibraryCollapsed, setNodeLibraryCollapsed] = useState<boolean>(false);
  const [propertiesPanelCollapsed, setPropertiesPanelCollapsed] = useState<boolean>(false);
  const [activeExecution, setActiveExecution] = useState<{isActive: boolean, executionId: string | null}>({isActive: false, executionId: null});
  const [showShortcutsModal, setShowShortcutsModal] = useState<boolean>(false);

  // State for plugin notification
  const [showPluginNotification, setShowPluginNotification] = useState(false);
  const [pluginCount, setPluginCount] = useState(0);

  // Disable WebSockets when used as a standalone component
  const standaloneMode = true; // Set to true when used outside of the main app
  if (standaloneMode) {
    FEATURES.WEBSOCKETS_ENABLED = false;
  }

  // Forward declarations of functions used in shortcut actions
  const handleNewWorkflow = () => {
    if (state.nodes.length > 0) {
      if (window.confirm('Are you sure you want to create a new workflow? Any unsaved changes will be lost.')) {
        setState({
          ...initialState,
          history: {
            past: [],
            future: []
          }
        });
      }
    } else {
      setState({
        ...initialState,
        history: {
          past: [],
          future: []
        }
      });
    }
  };

  // Undo action
  const undo = () => {
    if (state.history.past.length === 0) return;

    const previous = state.history.past[state.history.past.length - 1];
    const newPast = state.history.past.slice(0, state.history.past.length - 1);

    setState({
      ...previous,
      history: {
        past: newPast,
        future: [state, ...state.history.future]
      }
    });
  };

  // Redo action
  const redo = () => {
    if (state.history.future.length === 0) return;

    const next = state.history.future[0];
    const newFuture = state.history.future.slice(1);

    setState({
      ...next,
      history: {
        past: [...state.history.past, state],
        future: newFuture
      }
    });
  };

  // Handle saving the current workflow
  const handleSaveWorkflow = () => {
    try {
      // Save the workflow
      const workflowId = saveWorkflow(state.currentWorkflow);

      // Update the current workflow with the ID
      setState(prevState => ({
        ...prevState,
        currentWorkflow: {
          ...prevState.currentWorkflow,
          id: workflowId
        }
      }));

      // Show success message
      alert(`Workflow "${state.currentWorkflow.name}" saved successfully!`);
    } catch (error) {
      console.error('Error saving workflow:', error);
      alert(`Failed to save workflow: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Handle loading a workflow
  const handleLoadWorkflow = async () => {
    try {
      // Get all saved workflows
      const workflows = getSavedWorkflows();

      if (workflows.length === 0) {
        alert('No saved workflows found.');
        return;
      }

      // Show workflow selection dialog
      const selectedWorkflowId = await createWorkflowSelectionDialog(workflows);

      if (selectedWorkflowId) {
        // Load the selected workflow
        const selectedWorkflow = loadWorkflow(selectedWorkflowId);

        if (selectedWorkflow) {
          // Confirm if there are unsaved changes
          if (state.nodes.length > 0 && !confirm('Are you sure you want to load this workflow? Any unsaved changes will be lost.')) {
            return;
          }

          // Update the state with the loaded workflow
          setState({
            ...initialState,
            nodes: selectedWorkflow.nodes,
            connections: selectedWorkflow.connections,
            currentWorkflow: selectedWorkflow,
            currentNodeId: Math.max(...selectedWorkflow.nodes.map(n => {
              const idNum = parseInt(n.id.replace('node-', ''));
              return isNaN(idNum) ? 0 : idNum;
            }), 0) + 1,
            history: {
              past: [],
              future: []
            }
          });

          // Sync with demo mode if active
          if (isDemoMode) {
            updateDemoNodes(selectedWorkflow.nodes);
            updateDemoConnections(selectedWorkflow.connections);
          }

          // Show success message
          alert(`Workflow "${selectedWorkflow.name}" loaded successfully!`);
        }
      }
    } catch (error) {
      console.error('Error loading workflow:', error);
      alert(`Failed to load workflow: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Handle importing a workflow
  const handleImportWorkflow = (importedWorkflow: Workflow) => {
    try {
      // Confirm if there are unsaved changes
      if (state.nodes.length > 0 && !confirm('Are you sure you want to import this workflow? Any unsaved changes will be lost.')) {
        return;
      }

      // Update the state with the imported workflow
      setState({
        ...initialState,
        nodes: importedWorkflow.nodes,
        connections: importedWorkflow.connections,
        currentWorkflow: {
          ...importedWorkflow,
          id: null, // Ensure we're creating a new workflow
          name: `${importedWorkflow.name} (Imported)`
        },
        currentNodeId: Math.max(...importedWorkflow.nodes.map(n => {
          const idNum = parseInt(n.id.replace('node-', ''));
          return isNaN(idNum) ? 0 : idNum;
        }), 0) + 1,
        history: {
          past: [],
          future: []
        }
      });

      // Sync with demo mode if active
      if (isDemoMode) {
        updateDemoNodes(importedWorkflow.nodes);
        updateDemoConnections(importedWorkflow.connections);
      }

      // Show success message
      alert(`Workflow "${importedWorkflow.name}" imported successfully!`);
    } catch (error) {
      console.error('Error importing workflow:', error);
      alert(`Failed to import workflow: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Handle exporting the current workflow
  const handleExportWorkflow = () => {
    try {
      // Export the workflow
      exportWorkflow(state.currentWorkflow);
    } catch (error) {
      console.error('Error exporting workflow:', error);
      alert(`Failed to export workflow: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Define keyboard shortcut actions
  const shortcutActions = {
    newWorkflow: handleNewWorkflow,
    saveWorkflow: handleSaveWorkflow,
    openWorkflow: handleLoadWorkflow,
    undo,
    redo,
    showShortcuts: () => setShowShortcutsModal(true),
    zoomIn: () => {
      setState(prevState => ({
        ...prevState,
        zoom: {
          ...prevState.zoom,
          level: Math.min(prevState.zoom.level + prevState.zoom.step, prevState.zoom.max)
        }
      }));
    },
    zoomOut: () => {
      setState(prevState => ({
        ...prevState,
        zoom: {
          ...prevState.zoom,
          level: Math.max(prevState.zoom.level - prevState.zoom.step, prevState.zoom.min)
        }
      }));
    },
    zoomReset: () => {
      setState(prevState => ({
        ...prevState,
        zoom: {
          ...prevState.zoom,
          level: 1
        }
      }));
    },
    panUp: () => console.log('Pan up'),
    panDown: () => console.log('Pan down'),
    panLeft: () => console.log('Pan left'),
    panRight: () => console.log('Pan right'),
    deleteSelected: () => {
      if (state.selectedNode) {
        deleteNode(state.selectedNode);
      } else if (state.selectedConnection) {
        deleteConnection(state.selectedConnection);
      }
    },
    duplicateNode: () => {
      if (state.selectedNode) {
        const selectedNode = state.nodes.find(n => n.id === state.selectedNode);
        if (selectedNode) {
          const nodeId = addNode(selectedNode.type, selectedNode.x + 50, selectedNode.y + 50);
          const newNode = state.nodes.find(n => n.id === nodeId);
          if (newNode) {
            updateNodeConfig(nodeId, { ...selectedNode.config });
          }
        }
      }
    },
    selectAllNodes: () => {
      // Not implemented yet - would require multi-select functionality
      console.log('Select all nodes');
    },
    deselectAll: () => {
      selectNode(null);
    },
    editNode: () => {
      if (state.selectedNode) {
        openNodeEditor(state.selectedNode);
      }
    },
    executeWorkflow: () => setShowExecutionPanel(true),
    stopExecution: () => console.log('Stop execution'),
    toggleNodeLibrary: () => setNodeLibraryCollapsed(!nodeLibraryCollapsed),
    togglePropertiesPanel: () => setPropertiesPanelCollapsed(!propertiesPanelCollapsed),
    toggleAllPanels: () => {
      setNodeLibraryCollapsed(!nodeLibraryCollapsed);
      setPropertiesPanelCollapsed(!propertiesPanelCollapsed);
    },
    maximizeCanvas: () => {
      setNodeLibraryCollapsed(true);
      setPropertiesPanelCollapsed(true);
    },
    restorePanels: () => {
      setNodeLibraryCollapsed(false);
      setPropertiesPanelCollapsed(false);
    }
  };

  // Register keyboard shortcuts
  const shortcuts = getDefaultShortcuts(shortcutActions);
  useKeyboardShortcuts(shortcuts);

  // Load plugins from backend or use demo data
  useEffect(() => {
    const loadPlugins = async () => {
      try {
        if (isDemoMode) {
          // Use demo data
          setPlugins(demoPlugins);
          setState(prevState => ({
            ...prevState,
            nodes: demoNodes,
            connections: demoConnections,
            currentWorkflow: {
              ...prevState.currentWorkflow,
              nodes: demoNodes,
              connections: demoConnections
            }
          }));

          // Show notification for demo mode
          setPluginCount(demoPlugins.length);
          setShowPluginNotification(true);

          // Hide notification after 5 seconds
          setTimeout(() => {
            setShowPluginNotification(false);
          }, 5000);
        } else {
          // Refresh nodes from discovery service if available
          try {
            await refreshNodes();
          } catch (error) {
            console.warn('Failed to refresh nodes:', error);
          }

          // Legacy plugin loading for backward compatibility
          const fetchedPlugins = await getPlugins();

          // Handle different return types from getPlugins
          if (Array.isArray(fetchedPlugins)) {
            // If it's already an array of plugins, use it directly
            setPlugins(fetchedPlugins);
          } else if (fetchedPlugins && typeof fetchedPlugins === 'object') {
            // If it's a PluginResponse object, extract the plugins array
            const pluginsArray = fetchedPlugins.plugins || [];
            setPlugins(pluginsArray);
          } else {
            // Fallback to empty array
            setPlugins([]);
          }

          // Show notification if plugins were loaded
          const totalNodes = nodes.size;
          if (totalNodes > 0) {
            setPluginCount(totalNodes);
            setShowPluginNotification(true);

            // Hide notification after 5 seconds
            setTimeout(() => {
              setShowPluginNotification(false);
            }, 5000);
          }
        }
      } catch (error) {
        console.error('Failed to load plugins:', error);
      }
    };

    loadPlugins();
  }, [isDemoMode, demoNodes, demoConnections, demoPlugins]);

  // Add a node to the canvas
  const addNode = (type: string, x: number, y: number) => {
    const nodeId = `node-${state.currentNodeId}`;
    const newNode: NodeData = {
      id: nodeId,
      type,
      x,
      y,
      config: {}
    };

    const updatedState = {
      ...state,
      nodes: [...state.nodes, newNode],
      currentNodeId: state.currentNodeId + 1,
      currentWorkflow: {
        ...state.currentWorkflow,
        nodes: [...state.currentWorkflow.nodes, newNode]
      },
      history: {
        past: [...state.history.past, state],
        future: []
      }
    };

    setState(updatedState);

    // Sync with demo mode if active
    if (isDemoMode) {
      updateDemoNodes(updatedState.nodes);
    }

    return nodeId;
  };

  // Select a node
  const selectNode = (nodeId: string | null) => {
    setState(prevState => ({
      ...prevState,
      selectedNode: nodeId,
      selectedConnection: null
    }));
  };

  // Delete a node
  const deleteNode = (nodeId: string) => {
    // Remove connections related to this node
    const updatedConnections = state.connections.filter(
      conn => conn.from.nodeId !== nodeId && conn.to.nodeId !== nodeId
    );

    const updatedState = {
      ...state,
      nodes: state.nodes.filter(node => node.id !== nodeId),
      connections: updatedConnections,
      selectedNode: null,
      currentWorkflow: {
        ...state.currentWorkflow,
        nodes: state.currentWorkflow.nodes.filter(node => node.id !== nodeId),
        connections: updatedConnections
      },
      history: {
        past: [...state.history.past, state],
        future: []
      }
    };

    setState(updatedState);

    // Sync with demo mode if active
    if (isDemoMode) {
      updateDemoNodes(updatedState.nodes);
      updateDemoConnections(updatedState.connections);
    }
  };

  // Add a connection between nodes
  const addConnection = (fromNodeId: string, fromPort: string, toNodeId: string, toPort: string) => {
    const connectionId = `conn-${fromNodeId}-${fromPort}-${toNodeId}-${toPort}`;

    // Check if connection already exists
    const connectionExists = state.connections.some(
      conn => conn.from.nodeId === fromNodeId &&
              conn.from.port === fromPort &&
              conn.to.nodeId === toNodeId &&
              conn.to.port === toPort
    );

    if (connectionExists) return null;

    const newConnection: Connection = {
      id: connectionId,
      from: {
        nodeId: fromNodeId,
        port: fromPort
      },
      to: {
        nodeId: toNodeId,
        port: toPort
      }
    };

    const updatedState = {
      ...state,
      connections: [...state.connections, newConnection],
      currentWorkflow: {
        ...state.currentWorkflow,
        connections: [...state.currentWorkflow.connections, newConnection]
      },
      history: {
        past: [...state.history.past, state],
        future: []
      }
    };

    setState(updatedState);

    // Sync with demo mode if active
    if (isDemoMode) {
      updateDemoConnections(updatedState.connections);
    }

    return connectionId;
  };

  // Delete a connection
  const deleteConnection = (connectionId: string) => {
    const updatedState = {
      ...state,
      connections: state.connections.filter(conn => conn.id !== connectionId),
      selectedConnection: null,
      currentWorkflow: {
        ...state.currentWorkflow,
        connections: state.currentWorkflow.connections.filter(conn => conn.id !== connectionId)
      },
      history: {
        past: [...state.history.past, state],
        future: []
      }
    };

    setState(updatedState);

    // Sync with demo mode if active
    if (isDemoMode) {
      updateDemoConnections(updatedState.connections);
    }
  };

  // Update node configuration
  const updateNodeConfig = (nodeId: string, config: Record<string, any>) => {
    const updatedNodes = state.nodes.map(node =>
      node.id === nodeId ? { ...node, config } : node
    );

    const updatedState = {
      ...state,
      nodes: updatedNodes,
      currentWorkflow: {
        ...state.currentWorkflow,
        nodes: state.currentWorkflow.nodes.map(node =>
          node.id === nodeId ? { ...node, config } : node
        )
      },
      history: {
        past: [...state.history.past, state],
        future: []
      }
    };

    setState(updatedState);

    // Sync with demo mode if active
    if (isDemoMode) {
      updateDemoNodes(updatedNodes);
    }
  };

  // Track the last drag time to throttle history updates
  const lastDragTimeRef = useRef(0);
  const dragEndedRef = useRef(true);
  const pendingPositionRef = useRef<{nodeId: string, x: number, y: number} | null>(null);

  // Update node position with optimized performance
  const updateNodePosition = (nodeId: string, x: number, y: number) => {
    // Store the pending position
    pendingPositionRef.current = { nodeId, x, y };

    // Mark that we're dragging
    dragEndedRef.current = false;

    // Update the node position immediately without adding to history
    const updatedNodes = state.nodes.map(node =>
      node.id === nodeId ? { ...node, x, y } : node
    );

    setState(prevState => ({
      ...prevState,
      nodes: updatedNodes,
      currentWorkflow: {
        ...prevState.currentWorkflow,
        nodes: prevState.currentWorkflow.nodes.map(node =>
          node.id === nodeId ? { ...node, x, y } : node
        )
      }
    }));

    // Sync with demo mode if active (throttled to avoid excessive updates)
    if (isDemoMode) {
      const now = Date.now();
      if (now - lastDragTimeRef.current > 100) { // Throttle demo updates
        lastDragTimeRef.current = now;
        updateDemoNodes(updatedNodes);
      }
    }

    // Throttle history updates to avoid performance issues
    const now = Date.now();
    if (now - lastDragTimeRef.current > 500) { // Only update history every 500ms during drag
      lastDragTimeRef.current = now;

      // Add to history after throttling
      setState(prevState => ({
        ...prevState,
        history: {
          past: [...prevState.history.past, prevState],
          future: []
        }
      }));
    }

    // Set a timeout to detect when dragging has ended
    setTimeout(() => {
      dragEndedRef.current = true;

      // If we have a pending position and dragging has ended, update history
      if (pendingPositionRef.current && dragEndedRef.current) {
        const { nodeId, x, y } = pendingPositionRef.current;
        pendingPositionRef.current = null;

        // Final history update after drag ends
        setState(prevState => ({
          ...prevState,
          history: {
            past: [...prevState.history.past, prevState],
            future: []
          }
        }));

        // Final demo mode update
        if (isDemoMode) {
          updateDemoNodes(updatedNodes);
        }
      }
    }, 100);
  };

  // Open node editor
  const openNodeEditor = (nodeId: string) => {
    selectNode(nodeId);
    setShowNodeEditor(true);
  };

  // Clear the canvas
  const clearCanvas = () => {
    if (window.confirm('Are you sure you want to clear the canvas? This action cannot be undone.')) {
      const clearedState = {
        ...initialState,
        history: {
          past: [],
          future: []
        }
      };

      setState(clearedState);

      // Sync with demo mode if active
      if (isDemoMode) {
        updateDemoNodes([]);
        updateDemoConnections([]);
      }
    }
  };

  // handleNewWorkflow is defined above

  // Load a workflow from a template
  const handleLoadTemplate = (templateWorkflow: Workflow) => {
    if (state.nodes.length > 0) {
      if (window.confirm('Are you sure you want to load this template? Any unsaved changes will be lost.')) {
        // Create a new state with the template workflow
        setState({
          ...initialState,
          nodes: templateWorkflow.nodes,
          connections: templateWorkflow.connections,
          currentWorkflow: {
            ...templateWorkflow,
            id: null, // Ensure we're creating a new workflow
            name: `${templateWorkflow.name} Copy`
          },
          currentNodeId: Math.max(...templateWorkflow.nodes.map(n => {
            const idNum = parseInt(n.id.replace('node-', ''));
            return isNaN(idNum) ? 0 : idNum;
          }), 0) + 1,
          history: {
            past: [],
            future: []
          }
        });
      }
    } else {
      // Create a new state with the template workflow
      setState({
        ...initialState,
        nodes: templateWorkflow.nodes,
        connections: templateWorkflow.connections,
        currentWorkflow: {
          ...templateWorkflow,
          id: null, // Ensure we're creating a new workflow
          name: `${templateWorkflow.name} Copy`
        },
        currentNodeId: Math.max(...templateWorkflow.nodes.map(n => {
          const idNum = parseInt(n.id.replace('node-', ''));
          return isNaN(idNum) ? 0 : idNum;
        }), 0) + 1,
        history: {
          past: [],
          future: []
        }
      });
    }
  };

  // undo and redo are defined above

  return (
    <MockAuthProvider>
      <WebSocketProvider>
        <DndProvider backend={HTML5Backend}>
          <div className="container mx-auto relative">
            {/* Demo Mode Components - Only render when DemoModeProvider is available */}
            {hasDemoProvider.current && (
              <>
                <DemoModeToggle />
                <DemoWelcomeModal />
                {isDemoMode && <DemoFeedbackButton />}
                {isDemoMode && showDemoExecutionPanel && (
                  <DemoExecutionPanel onClose={() => setShowDemoExecutionPanel(false)} />
                )}
              </>
            )}
            {/* Execution Visualization Layer */}
            {activeExecution.isActive && (
              <ExecutionVisualization
                nodes={state.nodes}
                connections={state.connections}
                executionId={activeExecution.executionId}
                isExecuting={activeExecution.isActive}
              />
            )}
            {/* Plugin notification */}
            {showPluginNotification && (
              <div className="fixed top-4 right-4 bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded shadow-md z-50 animate-fade-in-out">
                <div className="flex items-center">
                  <div className="py-1">
                    <svg className="fill-current h-6 w-6 text-green-500 mr-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                      <path d="M2.93 17.07A10 10 0 1 1 17.07 2.93 10 10 0 0 1 2.93 17.07zm12.73-1.41A8 8 0 1 0 4.34 4.34a8 8 0 0 0 11.32 11.32zM9 11V9h2v6H9v-4zm0-6h2v2H9V5z"/>
                    </svg>
                  </div>
                  <div>
                    <p className="font-bold">Plugins Loaded</p>
                    <p className="text-sm">{pluginCount} plugins are now available in the sidebar.</p>
                  </div>
                  <button
                    onClick={() => setShowPluginNotification(false)}
                    className="ml-4 text-green-700 hover:text-green-900"
                  >
                    <svg className="h-4 w-4 fill-current" viewBox="0 0 20 20">
                      <path d="M10 8.586L2.929 1.515 1.515 2.929 8.586 10l-7.071 7.071 1.414 1.414L10 11.414l7.071 7.071 1.414-1.414L11.414 10l7.071-7.071-1.414-1.414L10 8.586z"/>
                    </svg>
                  </button>
                </div>
              </div>
            )}

            <WorkflowHeader
              workflowName={state.currentWorkflow.name}
              onNewWorkflow={handleNewWorkflow}
              onClearCanvas={clearCanvas}
              onSaveWorkflow={handleSaveWorkflow}
              onLoadWorkflow={handleLoadWorkflow}
              onImportWorkflow={handleImportWorkflow}
              onExportWorkflow={handleExportWorkflow}
              onLoadTemplate={handleLoadTemplate}
              onShowShortcuts={() => setShowShortcutsModal(true)}
            />

            <div className="flex flex-col h-full">
              <div className="flex flex-row h-full gap-4">
                {/* Node Library/Sidebar - Collapsible */}
                <div
                  className={`transition-all duration-300 ease-in-out bg-white rounded-lg shadow-md overflow-hidden flex flex-col ${nodeLibraryCollapsed ? 'w-12' : 'w-80'}`}
                >
                  {/* Collapsible Header */}
                  <div className="flex justify-between items-center p-3 border-b border-gray-200 bg-gray-50">
                    {!nodeLibraryCollapsed && (
                      <h3 className="font-medium text-gray-700">Node Library</h3>
                    )}
                    <button
                      className={`text-gray-500 hover:text-blue-600 p-1 rounded hover:bg-blue-50 ${nodeLibraryCollapsed ? 'mx-auto' : ''}`}
                      onClick={() => setNodeLibraryCollapsed(!nodeLibraryCollapsed)}
                      title={`${nodeLibraryCollapsed ? 'Expand' : 'Collapse'} Node Library (Alt+1)`}
                    >
                      <i className={`fas fa-chevron-${nodeLibraryCollapsed ? 'right' : 'left'}`}></i>
                    </button>
                  </div>

                  {/* Library Content - Only show when not collapsed */}
                  {!nodeLibraryCollapsed && (
                    <div className="flex-grow overflow-auto">
                      {showNodeLibrary ? (
                        <>
                          <NodeLibrary onRefresh={refreshNodes} />
                          <div className="mt-4 text-center pb-4">
                            <button
                              className="text-xs text-blue-600 hover:text-blue-800"
                              onClick={() => setShowNodeLibrary(false)}
                            >
                              Switch to legacy sidebar
                            </button>
                          </div>
                        </>
                      ) : (
                        <>
                          <ComponentSidebar plugins={plugins} />
                          <div className="mt-4 text-center pb-4">
                            <button
                              className="text-xs text-blue-600 hover:text-blue-800"
                              onClick={() => setShowNodeLibrary(true)}
                            >
                              Switch to new node library
                            </button>
                          </div>
                        </>
                      )}
                    </div>
                  )}

                  {/* Collapsed View - Show only icons */}
                  {nodeLibraryCollapsed && (
                    <div className="flex flex-col items-center py-4 space-y-6">
                      <button
                        className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center hover:bg-blue-200"
                        title="Control Flow Nodes"
                      >
                        <i className="fas fa-project-diagram"></i>
                      </button>
                      <button
                        className="w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center hover:bg-green-200"
                        title="Data Nodes"
                      >
                        <i className="fas fa-database"></i>
                      </button>
                      <button
                        className="w-8 h-8 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center hover:bg-purple-200"
                        title="Text Nodes"
                      >
                        <i className="fas fa-font"></i>
                      </button>
                      <button
                        className="w-8 h-8 rounded-full bg-yellow-100 text-yellow-600 flex items-center justify-center hover:bg-yellow-200"
                        title="Math Nodes"
                      >
                        <i className="fas fa-calculator"></i>
                      </button>
                    </div>
                  )}
                </div>

                {/* Main Canvas Area */}
                <div className="flex-grow flex flex-col bg-white rounded-lg shadow-md overflow-hidden">
                  {/* Toolbar */}
                  <div className="border-b p-4 flex justify-between items-center bg-white z-10">
                    <div className="flex items-center">
                      <input
                        type="text"
                        value={state.currentWorkflow.name}
                        onChange={(e) => setState(prevState => ({
                          ...prevState,
                          currentWorkflow: {
                            ...prevState.currentWorkflow,
                            name: e.target.value
                          }
                        }))}
                        className="border-b border-dashed border-gray-300 bg-transparent px-2 py-1 font-medium text-lg focus:outline-none focus:border-blue-500"
                      />
                    </div>

                    <div className="flex space-x-2">
                      <button
                        className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                        onClick={handleSaveWorkflow}
                        title="Save the current workflow (Ctrl+S)"
                      >
                        <i className="fas fa-save mr-1"></i> Save
                      </button>
                      <button
                        className="px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm"
                        onClick={handleLoadWorkflow}
                        title="Load a saved workflow (Ctrl+O)"
                      >
                        <i className="fas fa-folder-open mr-1"></i> Load
                      </button>
                      <button
                        className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                        onClick={() => {
                          if (isDemoMode) {
                            setShowDemoExecutionPanel(true);
                          } else {
                            setShowExecutionPanel(true);
                          }
                        }}
                        title="Execute the current workflow (F5)"
                      >
                        <i className="fas fa-play mr-1"></i> Execute
                      </button>
                      <button
                        className="px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 text-sm"
                        onClick={handleExportWorkflow}
                        title="Export the current workflow to a file"
                      >
                        <i className="fas fa-file-export mr-1"></i> Export
                      </button>
                      <button
                        className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                        onClick={clearCanvas}
                        title="Clear the canvas (Delete all nodes)"
                      >
                        <i className="fas fa-trash-alt mr-1"></i> Clear
                      </button>
                      <div className="border-l border-gray-300 mx-1"></div>
                      <button
                        className="px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 text-sm"
                        onClick={() => {
                          setNodeLibraryCollapsed(!nodeLibraryCollapsed);
                          setPropertiesPanelCollapsed(!propertiesPanelCollapsed);
                        }}
                        title="Toggle Panels"
                      >
                        <i className={`fas fa-${nodeLibraryCollapsed ? 'expand' : 'compress'} mr-1`}></i>
                        {nodeLibraryCollapsed ? 'Expand' : 'Collapse'} Panels
                        <span className="text-xs ml-1 opacity-70">(` key)</span>
                      </button>
                      <button
                        className={`px-3 py-1 ${showPropertiesPanel ? 'bg-blue-600' : 'bg-gray-600'} text-white rounded hover:bg-blue-700 text-sm`}
                        onClick={() => setShowPropertiesPanel(!showPropertiesPanel)}
                        title={showPropertiesPanel ? 'Hide Properties Panel' : 'Show Properties Panel'}
                      >
                        <i className="fas fa-sliders-h mr-1"></i> Properties
                      </button>
                    </div>
                  </div>

                  {/* Canvas */}
                  <div className="flex-grow flex overflow-hidden">
                    <WorkflowCanvas
                      nodes={state.nodes}
                      connections={state.connections}
                      selectedNode={state.selectedNode}
                      selectedConnection={state.selectedConnection}
                      zoom={state.zoom}
                      onAddNode={addNode}
                      onSelectNode={selectNode}
                      onDeleteNode={deleteNode}
                      onAddConnection={addConnection}
                      onDeleteConnection={deleteConnection}
                      onOpenNodeEditor={openNodeEditor}
                      onUndo={undo}
                      onRedo={redo}
                      onUpdateNodePosition={updateNodePosition}
                      onUpdateNodeConfig={updateNodeConfig}
                    />
                  </div>
                </div>

                {/* Properties Panel - Collapsible sidebar */}
                {showPropertiesPanel && (
                  <div
                    className={`transition-all duration-300 ease-in-out bg-white rounded-lg shadow-md overflow-hidden flex flex-col ${propertiesPanelCollapsed ? 'w-12' : 'w-96'} flex-shrink-0`}
                  >
                    {/* Collapsible Header */}
                    <div className="flex justify-between items-center p-3 border-b border-gray-200 bg-gray-50">
                      {!propertiesPanelCollapsed && (
                        <h3 className="font-medium text-gray-700">
                          {state.selectedNode ? 'Node Properties' : 'Properties'}
                        </h3>
                      )}
                      <button
                        className={`text-gray-500 hover:text-blue-600 p-1 rounded hover:bg-blue-50 ${propertiesPanelCollapsed ? 'mx-auto' : ''}`}
                        onClick={() => setPropertiesPanelCollapsed(!propertiesPanelCollapsed)}
                        title={`${propertiesPanelCollapsed ? 'Expand' : 'Collapse'} Properties Panel (Alt+2)`}
                      >
                        <i className={`fas fa-chevron-${propertiesPanelCollapsed ? 'left' : 'right'}`}></i>
                      </button>
                    </div>

                    {/* Properties Content - Only show when not collapsed */}
                    {!propertiesPanelCollapsed && (
                      <div className="flex-grow overflow-auto">
                        <PropertiesPanel
                          selectedNode={state.nodes.find(n => n.id === state.selectedNode)}
                          plugins={plugins}
                          onUpdateConfig={updateNodeConfig}
                        />
                      </div>
                    )}

                    {/* Collapsed View - Show only icons */}
                    {propertiesPanelCollapsed && (
                      <div className="flex flex-col items-center py-4 space-y-6">
                        {state.selectedNode ? (
                          <>
                            <button
                              className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center hover:bg-blue-200"
                              title="Edit Node"
                              onClick={() => openNodeEditor(state.selectedNode!)}
                            >
                              <i className="fas fa-edit"></i>
                            </button>
                            <button
                              className="w-8 h-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center hover:bg-red-200"
                              title="Delete Node"
                              onClick={() => deleteNode(state.selectedNode!)}
                            >
                              <i className="fas fa-trash"></i>
                            </button>
                          </>
                        ) : (
                          <div className="text-gray-400 text-xs text-center px-2 rotate-90 whitespace-nowrap">
                            Select a node
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Execution Panel */}
              {showExecutionPanel && (
                <ExecutionPanel
                  workflow={state.currentWorkflow}
                  nodes={state.nodes}
                  connections={state.connections}
                  onClose={() => setShowExecutionPanel(false)}
                  onVisualizationChange={(isActive, executionId) => {
                    setActiveExecution({isActive, executionId});
                  }}
                />
              )}
            </div>

            {showNodeEditor && state.selectedNode && (
              <NodeEditorModal
                nodeId={state.selectedNode}
                node={state.nodes.find(n => n.id === state.selectedNode)}
                plugins={plugins}
                onSave={(config) => {
                  if (state.selectedNode) {
                    updateNodeConfig(state.selectedNode, config);
                  }
                  setShowNodeEditor(false);
                }}
                onCancel={() => setShowNodeEditor(false)}
              />
            )}

            {/* Keyboard Shortcuts Modal */}
            {showShortcutsModal && (
              <KeyboardShortcutsModal
                shortcuts={shortcuts}
                onClose={() => setShowShortcutsModal(false)}
              />
            )}
          </div>
        </DndProvider>
      </WebSocketProvider>
    </MockAuthProvider>
  );
};

export default WorkflowBuilder;
