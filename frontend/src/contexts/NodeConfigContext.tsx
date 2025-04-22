import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getNodeConfigs } from '../services/api';

// Define the context type
export interface NodeConfigContextType {
  nodeConfigs: Record<string, any>;
  loading: boolean;
  error: string | null;
  refreshConfigs: () => Promise<void>;
  getConfigForNode: (nodeId: string) => any;
}

// Create the context
const NodeConfigContext = createContext<NodeConfigContextType | null>(null);

// Create a singleton instance of the context value
let contextInstance: NodeConfigContextType | null = null;

// Hook to use the context
export const useNodeConfig = (): NodeConfigContextType => {
  const context = useContext(NodeConfigContext);
  if (!context) {
    throw new Error('useNodeConfig must be used within a NodeConfigProvider');
  }
  return context;
};

// Initialize the node config service and create a context value
const initializeNodeConfigs = async (): Promise<NodeConfigContextType> => {
  try {
    console.log('Initializing node config service');
    
    // Fetch node configurations
    const configs = await getNodeConfigs();
    
    // Create the context value
    const value: NodeConfigContextType = {
      nodeConfigs: configs,
      loading: false,
      error: null,
      refreshConfigs: async () => {
        try {
          const updatedConfigs = await getNodeConfigs();
          value.nodeConfigs = updatedConfigs;
          value.error = null;
        } catch (error) {
          console.error('Error refreshing node configs:', error);
          value.error = 'Failed to refresh node configurations';
        }
      },
      getConfigForNode: (nodeId: string) => {
        return configs[nodeId] || null;
      }
    };
    
    // Store the context value in the singleton instance
    contextInstance = value;
    return value;
  } catch (error) {
    console.error('Error initializing node config service:', error);
    
    // Create a fallback context value
    const fallbackContext: NodeConfigContextType = {
      nodeConfigs: {},
      loading: false,
      error: 'Failed to load node configurations',
      refreshConfigs: async () => {
        try {
          const configs = await getNodeConfigs();
          fallbackContext.nodeConfigs = configs;
          fallbackContext.error = null;
        } catch (error) {
          console.error('Error refreshing node configs:', error);
          fallbackContext.error = 'Failed to refresh node configurations';
        }
      },
      getConfigForNode: () => null
    };
    
    return fallbackContext;
  }
};

// Initialize the context value immediately
initializeNodeConfigs().then(value => {
  console.log('Node config service initialized with', Object.keys(value.nodeConfigs).length, 'node configurations');
  contextInstance = value;
}).catch(error => {
  console.error('Failed to initialize node config service:', error);
});

// Provider component
export const NodeConfigProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [contextValue, setContextValue] = useState<NodeConfigContextType | null>(contextInstance);
  const [loading, setLoading] = useState(contextInstance === null);
  
  // Load context value if not already loaded
  useEffect(() => {
    if (contextInstance) {
      setContextValue(contextInstance);
      setLoading(false);
      return;
    }
    
    console.log('Initializing NodeConfigProvider from component');
    
    // Initialize the context value
    initializeNodeConfigs().then(value => {
      setContextValue(value);
      setLoading(false);
    }).catch(error => {
      console.error('Error initializing node config service:', error);
      setContextValue({
        nodeConfigs: {},
        loading: false,
        error: 'Failed to load node configurations',
        refreshConfigs: async () => {},
        getConfigForNode: () => null
      });
      setLoading(false);
    });
  }, []);
  
  // If still loading, show loading state
  if (loading) {
    return (
      <NodeConfigContext.Provider value={{
        nodeConfigs: {},
        loading: true,
        error: null,
        refreshConfigs: async () => {},
        getConfigForNode: () => null
      }}>
        {children}
      </NodeConfigContext.Provider>
    );
  }
  
  return (
    <NodeConfigContext.Provider value={contextValue!}>
      {children}
    </NodeConfigContext.Provider>
  );
};

export default NodeConfigContext;
