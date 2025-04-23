import React, { useEffect } from 'react';
import WorkflowBuilderWrapper from '../components/WorkflowBuilder/WorkflowBuilderWrapper';
import { NodeTypesProvider } from '../contexts/NodeTypesContext';
import { NodeDiscoveryProvider } from '../contexts/NodeDiscoveryContext';
import { WebSocketProvider } from '../contexts/WebSocketContext';
import { NodeConfigProvider } from '../contexts/NodeConfigContext';
import { DemoModeProvider } from '../contexts/DemoModeContext';
import DemoFeedbackButton from '../components/DemoMode/DemoFeedbackButton';

const DemoApp: React.FC = () => {
  // Use keys to force the providers to re-render
  const discoveryKey = 'node-discovery-provider-' + Date.now();
  const typesKey = 'node-types-provider-' + Date.now();

  // Check if we're in standalone mode
  const isStandalone = (window as any).STANDALONE_DEMO === true;

  // Add event listener for keyboard shortcuts
  useEffect(() => {
    // Add a keyboard shortcut to download the current workflow
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+S or Cmd+S to save workflow
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        alert('In the standalone demo, workflows are not saved. You can take a screenshot or use the browser\'s save functionality to save this page.');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="App">
      <DemoModeProvider>
        <WebSocketProvider>
          <NodeDiscoveryProvider key={discoveryKey}>
            <NodeTypesProvider key={typesKey}>
              <NodeConfigProvider>
                <div className="min-h-screen bg-gray-50">
                  {isStandalone && (
                    <div className="bg-blue-50 p-2 text-center">
                      <p className="text-sm text-blue-800">
                        <strong>Standalone Demo Mode</strong> - This demo runs entirely in your browser without a backend.
                        <button
                          className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-xs"
                          onClick={() => {
                            alert('Tips for using the Workflow Builder Demo:\n\n' +
                                  '1. Drag nodes from the left panel to the canvas\n' +
                                  '2. Connect nodes by dragging from output to input points\n' +
                                  '3. Configure nodes by clicking on them\n' +
                                  '4. Use the mouse wheel to zoom in/out\n' +
                                  '5. Press "C" to center the view\n' +
                                  '6. Press "Ctrl+F" to search for nodes\n' +
                                  '7. Right-click for context menu options');
                          }}
                        >
                          Show Tips
                        </button>
                      </p>
                    </div>
                  )}
                  <header className="bg-white shadow-sm">
                    <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
                      <div className="flex items-center">
                        <h1 className="text-2xl font-bold text-gray-900">Workflow Builder Demo</h1>
                        <span className="ml-3 inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                          Beta
                        </span>
                      </div>
                      <div>
                        <a
                          href="https://github.com/yourusername/workflow-builder"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-gray-500 hover:text-gray-700"
                        >
                          <i className="fab fa-github text-xl"></i>
                        </a>
                      </div>
                    </div>
                  </header>
                  <main>
                    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                      <WorkflowBuilderWrapper />
                    </div>
                  </main>
                  <footer className="bg-white mt-8 py-4 border-t border-gray-200">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                      <div className="flex flex-col items-center space-y-2">
                        <p className="text-center text-sm text-gray-500">
                          This is a demo version of the Workflow Builder. No data is saved between sessions.
                        </p>
                        {isStandalone && (
                          <div className="flex space-x-4 mt-2">
                            <button
                              className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-xs"
                              onClick={() => {
                                alert('Keyboard Shortcuts:\n\n' +
                                      'Scroll Wheel: Zoom in/out\n' +
                                      'Alt+Click or Middle-Click: Pan canvas\n' +
                                      'C: Center view\n' +
                                      'Ctrl+F or /: Search nodes\n' +
                                      'Alt+M: Toggle minimap\n' +
                                      'Right-Click: Context menu');
                              }}
                            >
                              <i className="fas fa-keyboard mr-1"></i> Keyboard Shortcuts
                            </button>
                            {/* Enhanced feedback button with modal */}
                            <DemoFeedbackButton />
                          </div>
                        )}
                      </div>
                    </div>
                  </footer>
                </div>
              </NodeConfigProvider>
            </NodeTypesProvider>
          </NodeDiscoveryProvider>
        </WebSocketProvider>
      </DemoModeProvider>
    </div>
  );
};

export default DemoApp;
