import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { createSampleWorkflow, mockPlugins, mockNodeTypes, mockExecuteWorkflow } from '../services/mockData';
import { NodeData, Connection, Plugin } from '../types';

interface DemoModeContextType {
  isDemoMode: boolean;
  toggleDemoMode: () => void;
  demoNodes: NodeData[];
  demoConnections: Connection[];
  demoPlugins: Plugin[];
  updateDemoNodes: (nodes: NodeData[]) => void;
  updateDemoConnections: (connections: Connection[]) => void;
  resetDemo: () => void;
  executeDemoWorkflow: () => Promise<any>;
  isExecuting: boolean;
  executionResults: any;
}

// Create default values for the context
const defaultDemoModeContext: DemoModeContextType = {
  isDemoMode: true,
  toggleDemoMode: () => {},
  demoNodes: [],
  demoConnections: [],
  demoPlugins: mockPlugins,
  updateDemoNodes: () => {},
  updateDemoConnections: () => {},
  resetDemo: () => {},
  executeDemoWorkflow: async () => ({}),
  isExecuting: false,
  executionResults: null
};

// Check if we're in GitHub Pages or standalone mode
const isStandalone =
  typeof window !== 'undefined' &&
  ((window as any).STANDALONE_DEMO === true ||
   window.location.hostname.includes('github.io') ||
   window.location.hostname.includes('netlify.app') ||
   window.location.hostname.includes('vercel.app'));

// Create the context with default values for standalone mode
const DemoModeContext = createContext<DemoModeContextType>(
  isStandalone ? defaultDemoModeContext : (undefined as any)
);

export const DemoModeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Force demo mode if we're in standalone mode
  const [isDemoMode, setIsDemoMode] = useState<boolean>(
    isStandalone || (window as any).FORCE_DEMO_MODE === true || false
  );
  const [demoNodes, setDemoNodes] = useState<NodeData[]>([]);
  const [demoConnections, setDemoConnections] = useState<Connection[]>([]);
  const [demoPlugins] = useState<Plugin[]>(mockPlugins);
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [executionResults, setExecutionResults] = useState<any>(null);

  // Initialize demo data when demo mode is enabled
  useEffect(() => {
    if (isDemoMode) {
      resetDemo();
    }
  }, [isDemoMode]);

  const toggleDemoMode = () => {
    if (!isStandalone) {
      setIsDemoMode(prev => !prev);
    }
  };

  const updateDemoNodes = (nodes: NodeData[]) => {
    setDemoNodes(nodes);
  };

  const updateDemoConnections = (connections: Connection[]) => {
    setDemoConnections(connections);
  };

  const resetDemo = () => {
    const { nodes, connections } = createSampleWorkflow();
    setDemoNodes(nodes);
    setDemoConnections(connections);
    setExecutionResults(null);
  };

  const executeDemoWorkflow = async () => {
    setIsExecuting(true);
    setExecutionResults(null);

    try {
      const results = await mockExecuteWorkflow(demoNodes, demoConnections);
      setExecutionResults(results);
      return results;
    } catch (error) {
      console.error('Error executing demo workflow:', error);
      throw error;
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <DemoModeContext.Provider
      value={{
        isDemoMode,
        toggleDemoMode,
        demoNodes,
        demoConnections,
        demoPlugins,
        updateDemoNodes,
        updateDemoConnections,
        resetDemo,
        executeDemoWorkflow,
        isExecuting,
        executionResults
      }}
    >
      {children}
    </DemoModeContext.Provider>
  );
};

export const useDemoMode = (): DemoModeContextType => {
  const context = useContext(DemoModeContext);

  // In standalone mode, we should never get undefined
  if (context === undefined) {
    console.warn('useDemoMode called outside of a DemoModeProvider');

    // If we're in standalone mode, return default context
    if (isStandalone) {
      return defaultDemoModeContext;
    }

    throw new Error('useDemoMode must be used within a DemoModeProvider');
  }

  return context;
};

// Export mock data for direct use
export { mockNodeTypes };
