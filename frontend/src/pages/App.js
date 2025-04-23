import React from 'react';
import WorkflowBuilder from '../components/WorkflowBuilder';
import { NodeDiscoveryProvider } from '../contexts/NodeDiscoveryContext';
import { NodeTypesProvider } from '../contexts/NodeTypesContext';
import { NodeConfigProvider } from '../contexts/NodeConfigContext';
import { WebSocketProvider } from '../contexts/WebSocketContext';
import { DemoModeProvider } from '../contexts/DemoModeContext';

function App() {
  return (
    <div className="App">
      <DemoModeProvider>
        <NodeDiscoveryProvider>
          <NodeTypesProvider>
            <NodeConfigProvider>
              <WebSocketProvider>
                <WorkflowBuilder />
              </WebSocketProvider>
            </NodeConfigProvider>
          </NodeTypesProvider>
        </NodeDiscoveryProvider>
      </DemoModeProvider>
    </div>
  );
}

export default App;
