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

const DemoModeContext = createContext<DemoModeContextType | undefined>(undefined);

export const DemoModeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isDemoMode, setIsDemoMode] = useState<boolean>(false);
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
    setIsDemoMode(prev => !prev);
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
  if (context === undefined) {
    throw new Error('useDemoMode must be used within a DemoModeProvider');
  }
  return context;
};

// Export mock data for direct use
export { mockNodeTypes };
