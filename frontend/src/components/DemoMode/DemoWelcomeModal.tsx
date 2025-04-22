import React, { useState, useEffect } from 'react';
import { useDemoMode } from '../../contexts/DemoModeContext';

const DemoWelcomeModal: React.FC = () => {
  const { isDemoMode } = useDemoMode();
  const [isOpen, setIsOpen] = useState(false);
  const [dontShowAgain, setDontShowAgain] = useState(false);

  useEffect(() => {
    // Show the modal when demo mode is enabled, unless user has chosen not to see it again
    if (isDemoMode && !localStorage.getItem('demoWelcomeModalDismissed')) {
      setIsOpen(true);
    } else {
      setIsOpen(false);
    }
  }, [isDemoMode]);

  const handleClose = () => {
    setIsOpen(false);
    if (dontShowAgain) {
      localStorage.setItem('demoWelcomeModalDismissed', 'true');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-800">
              Welcome to the Workflow Builder Demo!
            </h2>
            <button
              className="text-gray-500 hover:text-gray-700"
              onClick={handleClose}
            >
              <i className="fas fa-times"></i>
            </button>
          </div>

          <div className="prose max-w-none">
            <p className="text-gray-600">
              This is a standalone demo of our Workflow Builder UI. You can explore the interface and
              functionality without needing to set up a backend server.
            </p>

            <h3 className="text-lg font-semibold mt-4">What you can do in this demo:</h3>
            <ul className="list-disc pl-5 space-y-2">
              <li>Drag and drop nodes from the library onto the canvas</li>
              <li>Connect nodes by dragging from output to input points</li>
              <li>Configure node properties by clicking on them</li>
              <li>Pan the canvas by clicking and dragging (or Alt+Click)</li>
              <li>Zoom in/out using the mouse wheel</li>
              <li>Center the view with the "C" key or center button</li>
              <li>Search for nodes with Ctrl+F or "/" key</li>
              <li>Use the minimap for navigation (toggle with Alt+M)</li>
              <li>Right-click on the canvas for quick actions</li>
              <li>Execute the workflow to see simulated results</li>
            </ul>

            <h3 className="text-lg font-semibold mt-4">Keyboard Shortcuts:</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div><kbd className="px-2 py-1 bg-gray-100 rounded">Scroll</kbd> Zoom in/out</div>
              <div><kbd className="px-2 py-1 bg-gray-100 rounded">Alt+Click</kbd> Pan canvas</div>
              <div><kbd className="px-2 py-1 bg-gray-100 rounded">C</kbd> Center view</div>
              <div><kbd className="px-2 py-1 bg-gray-100 rounded">Ctrl+F</kbd> Search nodes</div>
              <div><kbd className="px-2 py-1 bg-gray-100 rounded">Alt+M</kbd> Toggle minimap</div>
              <div><kbd className="px-2 py-1 bg-gray-100 rounded">Right-Click</kbd> Context menu</div>
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-100">
              <h3 className="text-blue-800 font-medium">We'd love your feedback!</h3>
              <p className="text-blue-700 text-sm">
                This is a work in progress. Please try out the interface and let us know what you think.
                Your feedback will help us improve the workflow builder experience.
              </p>
            </div>
          </div>

          <div className="mt-6 flex items-center justify-between">
            <label className="flex items-center text-sm text-gray-600">
              <input
                type="checkbox"
                className="mr-2"
                checked={dontShowAgain}
                onChange={(e) => setDontShowAgain(e.target.checked)}
              />
              Don't show this again
            </label>
            <button
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              onClick={handleClose}
            >
              Get Started
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DemoWelcomeModal;
