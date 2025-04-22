import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getNodeTypes, getTypeSystem, getCoreNodes, checkTypeCompatibility } from '../services/api';
import { mockNodeTypes, mockTypeSystem } from '../data/mockData';

// Define types
export interface NodeTypePort {
  id: string;
  name: string;
  type: string;
  description?: string;
  required?: boolean;
  ui_properties?: {
    position?: string;
    [key: string]: any;
  };
}

export interface NodeTypeDefinition {
  id: string;
  name: string;
  category: string;
  description: string;
  inputs: NodeTypePort[];
  outputs: NodeTypePort[];
  ui_properties?: {
    color: string;
    icon: string;
    width?: number;
    [key: string]: any;
  };
}

export interface TypeRule {
  source: string;
  target: string[];
  bidirectional?: boolean;
}

export interface TypeDefinition {
  description: string;
  ui_properties: {
    color: string;
    icon: string;
    [key: string]: any;
  };
}

export interface TypeSystem {
  types: Record<string, TypeDefinition>;
  rules: TypeRule[];
}

interface NodeTypesContextType {
  nodeTypes: Record<string, NodeTypeDefinition>;
  typeSystem: TypeSystem;
  loading: boolean;
  error: string | null;
  isTypeCompatible: (sourceType: string, targetType: string) => Promise<boolean>;
  getPortType: (nodeType: string, portId: string, isInput: boolean) => string;
}

// Create context
const NodeTypesContext = createContext<NodeTypesContextType | undefined>(undefined);

// Create a singleton instance of the context value
let contextInstance: NodeTypesContextType | null = null;

// Initialize the node types service and create a context value
const initializeNodeTypes = async (): Promise<NodeTypesContextType> => {
  try {
    console.log('Initializing node types service directly');

    // Fetch core nodes
    let coreNodesData = [];
    try {
      coreNodesData = await getCoreNodes();
      console.log('Core nodes data:', coreNodesData);
    } catch (error) {
      console.error('Error fetching core nodes:', error);
      // Continue with empty core nodes
    }

    // Fetch plugins
    let pluginsData = null;
    try {
      pluginsData = await getNodeTypes();
      console.log('Plugins data:', pluginsData);
    } catch (error) {
      console.error('Error fetching plugins:', error);
      // Continue with null plugins
    }

    // Combine core nodes and plugins
    const combinedNodeTypes: Record<string, NodeTypeDefinition> = {};

    // Add core nodes
    if (Array.isArray(coreNodesData)) {
      console.log(`Adding ${coreNodesData.length} core nodes`);
      coreNodesData.forEach(node => {
        if (node && node.id) {
          // Ensure node has inputs and outputs arrays
          if (!node.inputs) node.inputs = [];
          if (!node.outputs) node.outputs = [];
          combinedNodeTypes[node.id] = node;
        }
      });
    }

    // Add plugins
    if (pluginsData && typeof pluginsData === 'object') {
      // Handle different response formats
      if (Array.isArray(pluginsData)) {
        console.log(`Adding ${pluginsData.length} plugins from array`);
        pluginsData.forEach(plugin => {
          if (plugin && plugin.id) {
            // Ensure plugin has inputs and outputs arrays
            if (!plugin.inputs) plugin.inputs = [];
            if (!plugin.outputs) plugin.outputs = [];
            combinedNodeTypes[plugin.id] = plugin;
          }
        });
      } else if (pluginsData.plugins && Array.isArray(pluginsData.plugins)) {
        console.log(`Adding ${pluginsData.plugins.length} plugins from object`);
        pluginsData.plugins.forEach((plugin: NodeTypeDefinition) => {
          if (plugin && plugin.id) {
            // Ensure plugin has inputs and outputs arrays
            if (!plugin.inputs) plugin.inputs = [];
            if (!plugin.outputs) plugin.outputs = [];
            combinedNodeTypes[plugin.id] = plugin;
          }
        });
      }
    }

    console.log(`Total node types: ${Object.keys(combinedNodeTypes).length}`);

    // If we didn't get any nodes, use fallback
    if (Object.keys(combinedNodeTypes).length === 0) {
      console.warn('No node types found, using fallback context');
      return createFallbackContext();
    }

    // Fetch type system
    let typeSystemData;
    try {
      typeSystemData = await getTypeSystem();
    } catch (error) {
      console.error('Error fetching type system:', error);
      // Use fallback type system
      typeSystemData = fallbackTypeSystem;
    }

    // Ensure all rules have the bidirectional property
    if (typeSystemData && typeSystemData.rules) {
      typeSystemData = {
        ...typeSystemData,
        rules: typeSystemData.rules.map(rule => ({
          ...rule,
          bidirectional: (rule as any).bidirectional || false
        }) as TypeRule)
      };
    } else {
      // If no type system data, use fallback
      typeSystemData = fallbackTypeSystem;
    }

    // Create the context value
    const value: NodeTypesContextType = {
      nodeTypes: combinedNodeTypes,
      typeSystem: typeSystemData as TypeSystem,
      loading: false,
      error: null,
      isTypeCompatible: async (sourceType: string, targetType: string): Promise<boolean> => {
        console.log(`Checking type compatibility: ${sourceType} -> ${targetType}`);

        // For development, always return true to allow any connections
        // This helps with testing the UI when the backend is not available
        return true;

        /* Uncomment this when backend is available
        // If types are the same, they're compatible
        if (sourceType === targetType) return true;

        // If either is 'any', they're compatible
        if (sourceType === 'any' || targetType === 'any') return true;

        try {
          // Use the API to check compatibility
          return await checkTypeCompatibility(sourceType, targetType);
        } catch (error) {
          console.error('Error checking type compatibility:', error);

          // Fallback to local check
          // Check type rules
          const rule = typeSystemData.rules.find(r => r.source === sourceType);
          if (rule && rule.target.includes(targetType)) return true;

          // Check bidirectional rules
          const bidirectionalRule = typeSystemData.rules.find(r =>
            r.source === targetType && !!(r as any).bidirectional && r.target.includes(sourceType)
          );
          if (bidirectionalRule) return true;

          return false;
        }
        */
      },
      getPortType: (nodeType: string, portId: string, isInput: boolean): string => {
        if (!nodeType || !portId) return 'any';

        const nodeDef = combinedNodeTypes[nodeType];
        if (!nodeDef) return 'any';

        const ports = isInput ? nodeDef.inputs : nodeDef.outputs;
        if (!ports || !Array.isArray(ports)) return 'any';

        const port = ports.find(p => p.id === portId || p.name === portId); // Support both id and name for backward compatibility

        return port?.type || 'any';
      }
    };

    // Store the context value in the singleton instance
    contextInstance = value;
    return value;
  } catch (error) {
    console.error('Error initializing node types service:', error);
    const fallbackContext = createFallbackContext();
    console.log('Using fallback context with', Object.keys(fallbackContext.nodeTypes).length, 'node types');
    return fallbackContext;
  }
};

// Initialize the context value immediately
initializeNodeTypes().then(value => {
  console.log('Node types service initialized with', Object.keys(value.nodeTypes).length, 'node types');
  contextInstance = value;
}).catch(error => {
  console.error('Failed to initialize node types service:', error);
});

// Provider component
export const NodeTypesProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [contextValue, setContextValue] = useState<NodeTypesContextType | null>(contextInstance);
  const [loading, setLoading] = useState(contextInstance === null);

  // Load context value if not already loaded
  useEffect(() => {
    if (contextInstance) {
      setContextValue(contextInstance);
      setLoading(false);
      return;
    }

    console.log('Initializing NodeTypesProvider from component');

    // Initialize the context value
    initializeNodeTypes().then(value => {
      setContextValue(value);
      setLoading(false);
    }).catch(error => {
      console.error('Error initializing node types service:', error);
      setContextValue(createFallbackContext());
      setLoading(false);
    });
  }, []);

  // If still loading, show loading state
  if (loading) {
    return (
      <NodeTypesContext.Provider value={createFallbackContext()}>
        {children}
      </NodeTypesContext.Provider>
    );
  }

  return (
    <NodeTypesContext.Provider value={contextValue || createFallbackContext()}>
      {children}
    </NodeTypesContext.Provider>
  );
};

// Fallback node types
const fallbackNodeTypes: Record<string, NodeTypeDefinition> = {
  'core.begin': {
    id: 'core.begin',
    name: 'Begin',
    category: 'CONTROL_FLOW',
    description: 'Starting point of the workflow',
    inputs: [],
    outputs: [
      { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'right-top' } },
      { id: 'workflow_id', name: 'Workflow ID', type: 'string', ui_properties: { position: 'right-center' } },
      { id: 'timestamp', name: 'Timestamp', type: 'number', ui_properties: { position: 'right-bottom' } }
    ],
    ui_properties: {
      color: '#2ecc71',
      icon: 'play',
      width: 240
    }
  },
  'core.end': {
    id: 'core.end',
    name: 'End',
    category: 'CONTROL_FLOW',
    description: 'Ending point of the workflow',
    inputs: [
      { id: 'trigger', name: 'Trigger', type: 'trigger', required: true, ui_properties: { position: 'left-top' } },
      { id: 'result', name: 'Result', type: 'any', ui_properties: { position: 'left-center' } }
    ],
    outputs: [
      { id: 'workflow_id', name: 'Workflow ID', type: 'string', ui_properties: { position: 'right-top' } },
      { id: 'execution_time', name: 'Execution Time', type: 'number', ui_properties: { position: 'right-center' } }
    ],
    ui_properties: {
      color: '#e74c3c',
      icon: 'stop',
      width: 240
    }
  },
  'core.text_input': {
    id: 'core.text_input',
    name: 'Text Input',
    category: 'TEXT',
    description: 'Enter text manually',
    inputs: [
      { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'left-top' } }
    ],
    outputs: [
      { id: 'text', name: 'Text', type: 'string', ui_properties: { position: 'right-top' } },
      { id: 'length', name: 'Length', type: 'number', ui_properties: { position: 'right-center' } }
    ],
    ui_properties: {
      color: '#3498db',
      icon: 'font',
      width: 240
    }
  },
  'core.text_output': {
    id: 'core.text_output',
    name: 'Text Output',
    category: 'TEXT',
    description: 'Display text results',
    inputs: [
      { id: 'text', name: 'Text', type: 'string', required: true, ui_properties: { position: 'left-top' } },
      { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'left-bottom' } }
    ],
    outputs: [
      { id: 'text', name: 'Text', type: 'string', ui_properties: { position: 'right-top' } }
    ],
    ui_properties: {
      color: '#e74c3c',
      icon: 'comment',
      width: 240
    }
  }
};

// Fallback type system
const fallbackTypeSystem: TypeSystem = {
  types: {
    'string': {
      description: 'A text value',
      ui_properties: {
        color: '#60a5fa',
        icon: 'font'
      }
    },
    'number': {
      description: 'A numeric value',
      ui_properties: {
        color: '#a78bfa',
        icon: 'hashtag'
      }
    },
    'boolean': {
      description: 'A true/false value',
      ui_properties: {
        color: '#f87171',
        icon: 'toggle-on'
      }
    },
    'object': {
      description: 'A JavaScript object',
      ui_properties: {
        color: '#4ade80',
        icon: 'cube'
      }
    },
    'array': {
      description: 'An array of values',
      ui_properties: {
        color: '#fbbf24',
        icon: 'list'
      }
    },
    'any': {
      description: 'Any type of value',
      ui_properties: {
        color: '#9ca3af',
        icon: 'asterisk'
      }
    },
    'trigger': {
      description: 'A workflow trigger signal',
      ui_properties: {
        color: '#ec4899',
        icon: 'bolt'
      }
    }
  },
  rules: [
    { source: 'string', target: ['string', 'any'], bidirectional: false },
    { source: 'number', target: ['number', 'string', 'any'], bidirectional: false },
    { source: 'boolean', target: ['boolean', 'string', 'any'], bidirectional: false },
    { source: 'object', target: ['object', 'any'], bidirectional: false },
    { source: 'array', target: ['array', 'any'], bidirectional: false },
    { source: 'trigger', target: ['trigger'], bidirectional: true },
    { source: 'any', target: ['string', 'number', 'boolean', 'object', 'array', 'any'], bidirectional: true }
  ]
};

// Create fallback context
const createFallbackContext = (): NodeTypesContextType => {
  // Combine fallback node types with mock data
  const combinedNodeTypes: Record<string, NodeTypeDefinition> = {
    ...fallbackNodeTypes
  };

  // Add core nodes from mock data
  if (mockNodeTypes && mockNodeTypes.coreNodes) {
    mockNodeTypes.coreNodes.forEach((node: any) => {
      if (!combinedNodeTypes[node.id]) {
        combinedNodeTypes[node.id] = node;
      }
    });
  }

  // Add plugins from mock data
  if (mockNodeTypes && mockNodeTypes.plugins) {
    mockNodeTypes.plugins.forEach((plugin: any) => {
      if (!combinedNodeTypes[plugin.id]) {
        combinedNodeTypes[plugin.id] = plugin;
      }
    });
  }

  console.log(`Created fallback node types context with ${Object.keys(combinedNodeTypes).length} node types`);

  return {
    nodeTypes: combinedNodeTypes,
    typeSystem: fallbackTypeSystem,
    loading: false,
    error: null,
    isTypeCompatible: async (sourceType: string, targetType: string): Promise<boolean> => {
      console.log(`Fallback context checking type compatibility: ${sourceType} -> ${targetType}`);

      // For development, always return true to allow any connections
      // This helps with testing the UI when the backend is not available
      return true;

      /* Uncomment this when backend is available
      // If types are the same, they're compatible
      if (sourceType === targetType) return true;

      // If either is 'any', they're compatible
      if (sourceType === 'any' || targetType === 'any') return true;

      // Check type rules
      const rule = fallbackTypeSystem.rules.find(r => r.source === sourceType);
      if (rule && rule.target.includes(targetType)) return true;

      // Check bidirectional rules
      const bidirectionalRule = fallbackTypeSystem.rules.find(r =>
        r.source === targetType && !!(r as any).bidirectional && r.target.includes(sourceType)
      );
      if (bidirectionalRule) return true;

      return false;
      */
    },
    getPortType: (nodeType: string, portId: string, isInput: boolean): string => {
      if (!nodeType || !portId) return 'any';

      const nodeDef = combinedNodeTypes[nodeType];
      if (!nodeDef) return 'any';

      const ports = isInput ? nodeDef.inputs : nodeDef.outputs;
      const port = ports?.find(p => p.id === portId || p.name === portId);

      return port?.type || 'any';
    }
  };
};

// Create a static fallback context instance
let fallbackContextInstance: NodeTypesContextType | null = null;

// Hook for using the context
export const useNodeTypes = (): NodeTypesContextType => {
  // First try to get the context from React's context mechanism
  const context = useContext(NodeTypesContext);

  // If the context is available, use it
  if (context !== undefined) {
    return context;
  }

  // If the context is not available but we have a singleton instance, use that
  if (contextInstance !== null) {
    console.warn('Using singleton instance of NodeTypesContext instead of React context');
    return contextInstance;
  }

  // If we have a fallback context instance, use that
  if (fallbackContextInstance !== null) {
    return fallbackContextInstance;
  }

  // If neither is available, create a fallback context
  console.warn('NodeTypesContext not available, using fallback values');
  fallbackContextInstance = createFallbackContext();
  return fallbackContextInstance;
};
