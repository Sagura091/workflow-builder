import React from 'react';
import WorkflowBuilder from './components/WorkflowBuilder';
import { NodeDiscoveryProvider } from './contexts/NodeDiscoveryContext';
import { NodeTypesProvider } from './contexts/NodeTypesContext';
import { NodeConfigProvider } from './contexts/NodeConfigContext';
import { WebSocketProvider } from './contexts/WebSocketContext';

function App() {
  return (
    <div className="App">
      <NodeDiscoveryProvider>
        <NodeTypesProvider>
          <NodeConfigProvider>
            <WebSocketProvider>
              <WorkflowBuilder />
            </WebSocketProvider>
          </NodeConfigProvider>
        </NodeTypesProvider>
      </NodeDiscoveryProvider>
    </div>
  );
}

export default App;
