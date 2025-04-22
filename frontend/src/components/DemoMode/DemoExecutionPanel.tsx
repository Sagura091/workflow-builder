import React, { useState } from 'react';
import { useDemoMode } from '../../contexts/DemoModeContext';

const DemoExecutionPanel: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  const { executeDemoWorkflow, isExecuting, executionResults } = useDemoMode();
  const [activeTab, setActiveTab] = useState<'results' | 'logs'>('results');

  const handleExecute = async () => {
    try {
      await executeDemoWorkflow();
    } catch (error) {
      console.error('Error executing workflow:', error);
    }
  };

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl h-[80vh] flex flex-col">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-800">Workflow Execution</h2>
          <button
            className="text-gray-500 hover:text-gray-700"
            onClick={onClose}
          >
            <i className="fas fa-times"></i>
          </button>
        </div>

        <div className="flex border-b border-gray-200">
          <button
            className={`px-4 py-2 font-medium ${
              activeTab === 'results'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
            onClick={() => setActiveTab('results')}
          >
            Results
          </button>
          <button
            className={`px-4 py-2 font-medium ${
              activeTab === 'logs'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
            onClick={() => setActiveTab('logs')}
          >
            Logs
          </button>
        </div>

        <div className="flex-grow overflow-auto p-4">
          {isExecuting ? (
            <div className="h-full flex flex-col items-center justify-center">
              <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
              <p className="mt-4 text-gray-600">Executing workflow...</p>
            </div>
          ) : executionResults ? (
            activeTab === 'results' ? (
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-800">Node Outputs</h3>
                {Object.entries(executionResults.results.node_outputs).map(([nodeId, output]) => (
                  <div key={nodeId} className="border border-gray-200 rounded-lg p-4">
                    <div className="font-medium text-gray-700 mb-2">Node: {nodeId}</div>
                    <pre className="bg-gray-50 p-3 rounded text-sm overflow-auto max-h-40">
                      {JSON.stringify(output, null, 2)}
                    </pre>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-800">Execution Logs</h3>
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Timestamp
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Node
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Message
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {executionResults.results.log.map((log: any, index: number) => (
                        <tr key={index}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(log.timestamp).toLocaleTimeString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {log.node}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {log.message}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-gray-500">
              <i className="fas fa-play-circle text-5xl mb-4"></i>
              <p>Click "Execute Workflow" to see results</p>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-gray-200 flex justify-end">
          <button
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 mr-2"
            onClick={onClose}
          >
            Close
          </button>
          <button
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 flex items-center"
            onClick={handleExecute}
            disabled={isExecuting}
          >
            {isExecuting ? (
              <>
                <i className="fas fa-spinner fa-spin mr-2"></i> Executing...
              </>
            ) : (
              <>
                <i className="fas fa-play mr-2"></i> Execute Workflow
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DemoExecutionPanel;
