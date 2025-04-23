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
   window.location.hostname.includes('vercel.app') ||
   window.location.hostname === 'localhost' ||
   window.location.search.includes('demo=true'));

// Log demo mode status
if (isStandalone) {
  console.log('Running in standalone demo mode');
}

// Create the context with default values for standalone mode
const DemoModeContext = createContext<DemoModeContextType>(
  isStandalone ? defaultDemoModeContext : (undefined as any)
);

export const DemoModeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Load demo mode state from localStorage or use default
  const loadDemoModeState = (): boolean => {
    // Always use demo mode in standalone mode
    if (isStandalone || (window as any).FORCE_DEMO_MODE === true) {
      return true;
    }

    // Check localStorage for saved preference
    const savedState = localStorage.getItem('demo_mode_enabled');
    if (savedState !== null) {
      return savedState === 'true';
    }

    // Default to false in regular development mode
    return false;
  };

  const [isDemoMode, setIsDemoMode] = useState<boolean>(loadDemoModeState());

  // Initialize with sample workflow data
  const sampleWorkflow = createSampleWorkflow();
  const [demoNodes, setDemoNodes] = useState<NodeData[]>(sampleWorkflow.nodes);
  const [demoConnections, setDemoConnections] = useState<Connection[]>(sampleWorkflow.connections);
  const [demoPlugins] = useState<Plugin[]>(mockPlugins);
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [executionResults, setExecutionResults] = useState<any>(null);

  // Log that demo mode is active
  useEffect(() => {
    if (isDemoMode) {
      console.log('Demo mode is active');
      console.log('Sample workflow loaded with', demoNodes.length, 'nodes and', demoConnections.length, 'connections');
    }
  }, [isDemoMode, demoNodes.length, demoConnections.length]);

  // Initialize demo data when demo mode is enabled
  useEffect(() => {
    if (isDemoMode) {
      resetDemo();
    }
  }, [isDemoMode]);

  // Save demo mode state to localStorage whenever it changes
  useEffect(() => {
    // Don't save in standalone mode since it's always true
    if (!isStandalone) {
      localStorage.setItem('demo_mode_enabled', String(isDemoMode));
    }
  }, [isDemoMode]);

  const toggleDemoMode = () => {
    // Allow toggling in development mode even if we're in standalone mode
    if (!isStandalone || process.env.NODE_ENV === 'development') {
      const newDemoMode = !isDemoMode;

      // Update state
      setIsDemoMode(newDemoMode);

      // Save to localStorage
      localStorage.setItem('demo_mode_enabled', String(newDemoMode));

      console.log('Demo mode toggled to:', newDemoMode);
    } else {
      console.warn('Cannot toggle demo mode in standalone production mode');
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
      // Show a loading message
      console.log('Executing demo workflow...');

      // Execute the workflow with the current nodes and connections
      const results = await mockExecuteWorkflow(demoNodes, demoConnections);

      // Log the results
      console.log('Workflow execution completed:', results);

      // Update the state with the results
      setExecutionResults(results);

      // Show a success message
      if (isStandalone) {
        // In standalone mode, show a more detailed message
        alert('Workflow executed successfully! This is a simulated execution in the demo mode. In a real implementation, this would connect to a backend service to execute the workflow.');
      }

      return results;
    } catch (error) {
      console.error('Error executing demo workflow:', error);

      // Show an error message
      if (isStandalone) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        alert(`Error executing workflow: ${errorMessage}. This is a simulated error in the demo mode.`);
      }

      throw error;
    } finally {
      setIsExecuting(false);
    }
  };

  // Create the context value object
  const contextValue = {
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
  };

  // Expose the context to the window object for development tools
  if (process.env.NODE_ENV === 'development') {
    (window as any).__DEMO_MODE_CONTEXT__ = contextValue;
  }

  return (
    <DemoModeContext.Provider value={contextValue}>
      {children}
    </DemoModeContext.Provider>
  );
};

export const useDemoMode = (): DemoModeContextType => {
  const context = useContext(DemoModeContext);

  // In standalone mode, we should never get undefined
  if (context === undefined) {
    console.warn('useDemoMode called outside of a DemoModeProvider');

    // Check if we're in standalone mode or if the global flag is set
    if (isStandalone || (window as any).FORCE_DEMO_MODE === true || (window as any).ENSURE_DEMO_MODE_PROVIDER === true) {
      console.log('Using fallback demo context');
      return defaultDemoModeContext;
    }

    // Only throw if we're not in any kind of demo mode
    throw new Error('useDemoMode must be used within a DemoModeProvider');
  }

  return context;
};

// Export mock data for direct use
export { mockNodeTypes };
