import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import nodeDiscoveryService, { DiscoveredNode } from '../services/nodeDiscovery';
import { mockNodeTypes } from '../data/mockData';

// Define NodeStatus enum for use in fallback values
enum NodeStatusEnum {
  Available = 'available',
  Error = 'error',
  Deprecated = 'deprecated',
  Experimental = 'experimental'
}

// Define context type
interface NodeDiscoveryContextType {
  nodes: Map<string, DiscoveredNode>;
  nodesByCategory: Record<string, DiscoveredNode[]>;
  loading: boolean;
  error: string | null;
  refreshNodes: () => Promise<boolean>;
  getNodeById: (id: string) => DiscoveredNode | undefined;
  getNodesByStatus: (status: string) => DiscoveredNode[];
}

// Create context
const NodeDiscoveryContext = createContext<NodeDiscoveryContextType | undefined>(undefined);

// Create a singleton instance of the context value
let contextInstance: NodeDiscoveryContextType | null = null;

// Initialize the node discovery service and create a context value
const initializeNodeDiscovery = async (): Promise<NodeDiscoveryContextType> => {
  try {
    console.log('Initializing node discovery service directly');

    // Discover nodes
    const discoveredNodes = await nodeDiscoveryService.discoverNodes();
    const nodesByCategory = nodeDiscoveryService.getNodesByCategory();

    // Check if we got any nodes
    if (discoveredNodes.size === 0 || Object.keys(nodesByCategory).length === 0) {
      console.warn('No nodes discovered from service, using fallback data');
      return createFallbackContext();
    }

    console.log(`Discovered ${discoveredNodes.size} nodes in ${Object.keys(nodesByCategory).length} categories`);
    console.log('Categories:', Object.keys(nodesByCategory));

    // Create context value
    const value: NodeDiscoveryContextType = {
      nodes: discoveredNodes,
      nodesByCategory,
      loading: false,
      error: null,
      refreshNodes: async () => {
        try {
          await nodeDiscoveryService.discoverNodes();
          return true;
        } catch (error) {
          console.error('Error refreshing nodes:', error);
          return false;
        }
      },
      getNodeById: (id: string) => discoveredNodes.get(id),
      getNodesByStatus: (status: string) => {
        const result: DiscoveredNode[] = [];
        discoveredNodes.forEach(node => {
          if (node.status === status) {
            result.push(node);
          }
        });
        return result;
      }
    };

    // Store the context value in the singleton instance
    contextInstance = value;
    return value;
  } catch (error) {
    console.error('Error initializing node discovery service:', error);
    const fallbackContext = createFallbackContext();
    console.log('Using fallback context with', fallbackContext.nodes.size, 'nodes');
    return fallbackContext;
  }
};

// Initialize the context value immediately
initializeNodeDiscovery().then(value => {
  console.log('Node discovery service initialized with', value.nodes.size, 'nodes');
  contextInstance = value;
}).catch(error => {
  console.error('Failed to initialize node discovery service:', error);
});

// Provider component
export const NodeDiscoveryProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [contextValue, setContextValue] = useState<NodeDiscoveryContextType | null>(contextInstance);
  const [loading, setLoading] = useState(contextInstance === null);

  // Load context value if not already loaded
  useEffect(() => {
    if (contextInstance) {
      setContextValue(contextInstance);
      setLoading(false);
      return;
    }

    console.log('Initializing NodeDiscoveryProvider from component');

    // Initialize the context value
    initializeNodeDiscovery().then(value => {
      setContextValue(value);
      setLoading(false);
    }).catch(error => {
      console.error('Error initializing node discovery service:', error);
      setContextValue(createFallbackContext());
      setLoading(false);
    });

    // Subscribe to node changes
    const unsubscribe = nodeDiscoveryService.addListener(() => {
      const updatedValue = {
        ...contextInstance!,
        nodes: new Map(nodeDiscoveryService.getNodes()),
        nodesByCategory: nodeDiscoveryService.getNodesByCategory()
      };
      setContextValue(updatedValue);
      contextInstance = updatedValue;
    });

    return () => {
      unsubscribe();
    };
  }, []);

  // If still loading, show loading state
  if (loading) {
    return (
      <NodeDiscoveryContext.Provider value={createFallbackContext()}>
        {children}
      </NodeDiscoveryContext.Provider>
    );
  }

  return (
    <NodeDiscoveryContext.Provider value={contextValue || createFallbackContext()}>
      {children}
    </NodeDiscoveryContext.Provider>
  );
};

// Fallback values for when the context is not available
const fallbackNodes: DiscoveredNode[] = [
  {
    id: 'core.begin',
    name: 'Begin',
    category: 'CONTROL_FLOW',
    description: 'Starting point of the workflow',
    status: NodeStatusEnum.Available,
    isCore: true,
    inputs: [],
    outputs: [
      { id: 'trigger', name: 'Trigger', type: 'trigger' },
      { id: 'workflow_id', name: 'Workflow ID', type: 'string' },
      { id: 'timestamp', name: 'Timestamp', type: 'number' }
    ],
    ui_properties: {
      color: '#2ecc71',
      icon: 'play',
      width: 240
    }
  },
  {
    id: 'core.end',
    name: 'End',
    category: 'CONTROL_FLOW',
    description: 'Ending point of the workflow',
    status: NodeStatusEnum.Available,
    isCore: true,
    inputs: [
      { id: 'trigger', name: 'Trigger', type: 'trigger', required: true },
      { id: 'result', name: 'Result', type: 'any' }
    ],
    outputs: [
      { id: 'workflow_id', name: 'Workflow ID', type: 'string' },
      { id: 'execution_time', name: 'Execution Time', type: 'number' }
    ],
    ui_properties: {
      color: '#e74c3c',
      icon: 'stop',
      width: 240
    }
  },
  {
    id: 'core.text_input',
    name: 'Text Input',
    category: 'TEXT',
    description: 'Enter text manually',
    status: NodeStatusEnum.Available,
    isCore: true,
    inputs: [
      { id: 'trigger', name: 'Trigger', type: 'trigger' }
    ],
    outputs: [
      { id: 'text', name: 'Text', type: 'string' },
      { id: 'length', name: 'Length', type: 'number' }
    ],
    ui_properties: {
      color: '#3498db',
      icon: 'font',
      width: 240
    }
  },
  {
    id: 'core.text_output',
    name: 'Text Output',
    category: 'TEXT',
    description: 'Display text results',
    status: NodeStatusEnum.Available,
    isCore: true,
    inputs: [
      { id: 'text', name: 'Text', type: 'string', required: true },
      { id: 'trigger', name: 'Trigger', type: 'trigger' }
    ],
    outputs: [
      { id: 'text', name: 'Text', type: 'string' }
    ],
    ui_properties: {
      color: '#e74c3c',
      icon: 'comment',
      width: 240
    }
  }
];

// Create fallback context value
const createFallbackContext = (): NodeDiscoveryContextType => {
  try {
    // Create nodes from mock data
    const allNodes: DiscoveredNode[] = [
      ...fallbackNodes
    ];

    // Add core nodes from mock data if available
    if (mockNodeTypes && mockNodeTypes.coreNodes && Array.isArray(mockNodeTypes.coreNodes)) {
      allNodes.push(...mockNodeTypes.coreNodes.map((node: any) => ({
        id: node.id,
        name: node.name,
        description: node.description || '',
        category: node.category || 'Core',
        status: NodeStatusEnum.Available,
        statusMessage: '',
        isCore: true,
        inputs: node.inputs || [],
        outputs: node.outputs || [],
        ui_properties: node.ui_properties || {}
      })));
    }

    // Add plugins from mock data if available
    if (mockNodeTypes && mockNodeTypes.plugins && Array.isArray(mockNodeTypes.plugins)) {
      allNodes.push(...mockNodeTypes.plugins.map((plugin: any) => ({
        id: plugin.id,
        name: plugin.name,
        description: plugin.description || '',
        category: plugin.category || 'Plugins',
        status: NodeStatusEnum.Available,
        statusMessage: '',
        isCore: false,
        inputs: plugin.inputs || [],
        outputs: plugin.outputs || [],
        ui_properties: plugin.ui_properties || {}
      })));
    }

    const nodesMap = new Map<string, DiscoveredNode>();
    const nodesByCategory: Record<string, DiscoveredNode[]> = {};

    // Ensure we have at least these categories
    nodesByCategory['CONTROL_FLOW'] = [];
    nodesByCategory['TEXT'] = [];
    nodesByCategory['DATA'] = [];
    nodesByCategory['MATH'] = [];

    // Populate the map and categories
    allNodes.forEach(node => {
      if (!node || !node.id) {
        console.warn('Invalid node in fallback data');
        return;
      }

      nodesMap.set(node.id, node);

      const category = node.category || 'Uncategorized';
      if (!nodesByCategory[category]) {
        nodesByCategory[category] = [];
      }
      nodesByCategory[category].push(node);
    });

    console.log(`Created fallback context with ${nodesMap.size} nodes in ${Object.keys(nodesByCategory).length} categories`);
    console.log('Categories:', Object.keys(nodesByCategory));
    console.log('Nodes by category:', nodesByCategory);

    return {
      nodes: nodesMap,
      nodesByCategory,
      loading: false,
      error: null,
      refreshNodes: async () => true, // Return true to indicate success
      getNodeById: (id: string) => nodesMap.get(id),
      getNodesByStatus: (status: string) => {
        return Array.from(nodesMap.values()).filter(node => node.status === status);
      }
    };
  } catch (error) {
    console.error('Error creating fallback context:', error);

    // Create a minimal fallback context with just the hardcoded nodes
    const nodesMap = new Map<string, DiscoveredNode>();
    const nodesByCategory: Record<string, DiscoveredNode[]> = {
      'CONTROL_FLOW': [],
      'TEXT': []
    };

    // Add fallback nodes
    fallbackNodes.forEach(node => {
      nodesMap.set(node.id, node);
      const category = node.category || 'Uncategorized';
      if (!nodesByCategory[category]) {
        nodesByCategory[category] = [];
      }
      nodesByCategory[category].push(node);
    });

    return {
      nodes: nodesMap,
      nodesByCategory,
      loading: false,
      error: 'Failed to load nodes. Using minimal fallback data.',
      refreshNodes: async () => true,
      getNodeById: (id: string) => nodesMap.get(id),
      getNodesByStatus: (status: string) => {
        return Array.from(nodesMap.values()).filter(node => node.status === status);
      }
    };
  }
};

// Create a static fallback context instance
let fallbackContextInstance: NodeDiscoveryContextType | null = null;

// Hook for using the context
export const useNodeDiscovery = (): NodeDiscoveryContextType => {
  // First try to get the context from React's context mechanism
  const context = useContext(NodeDiscoveryContext);

  // If the context is available, use it
  if (context !== undefined) {
    return context;
  }

  // If the context is not available but we have a singleton instance, use that
  if (contextInstance !== null) {
    console.warn('Using singleton instance of NodeDiscoveryContext instead of React context');
    return contextInstance;
  }

  // If we have a fallback context instance, use that
  if (fallbackContextInstance !== null) {
    return fallbackContextInstance;
  }

  // If neither is available, create a fallback context
  console.warn('NodeDiscoveryProvider not available, using fallback values');
  fallbackContextInstance = createFallbackContext();
  return fallbackContextInstance;
};
