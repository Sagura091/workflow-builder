import React, { useState, useEffect } from 'react';
import { useDemoMode } from '../../contexts/DemoModeContext';
import { FEATURES } from '../../config';

/**
 * A component that provides a convenient way to toggle between demo mode and real implementation
 * during development.
 */
const DevelopmentModeToggle: React.FC = () => {
  const { isDemoMode, toggleDemoMode, resetDemo } = useDemoMode();
  const [isVisible, setIsVisible] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState<'demo' | 'features' | 'debug'>('demo');
  const [showNotification, setShowNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');

  // Check if we're in development mode
  const isDevelopment = process.env.NODE_ENV === 'development';

  // Don't show in production unless forced
  useEffect(() => {
    const forceDevTools = localStorage.getItem('force_dev_tools') === 'true';
    if (!isDevelopment && !forceDevTools) {
      setIsVisible(false);
    }
  }, [isDevelopment]);

  // Handle toggling demo mode
  const handleToggleDemoMode = () => {
    toggleDemoMode();

    // Show notification
    const newDemoMode = !isDemoMode;
    setNotificationMessage(`Demo Mode ${newDemoMode ? 'Enabled' : 'Disabled'}`);
    setShowNotification(true);

    // Hide notification after 2 seconds
    setTimeout(() => {
      setShowNotification(false);
    }, 2000);

    // If we're switching to demo mode, reset the demo data
    if (newDemoMode) {
      resetDemo();
    }
  };

  // Add keyboard shortcut for toggling demo mode (Alt+D)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.altKey && e.key === 'd') {
        handleToggleDemoMode();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isDemoMode]);

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Notification */}
      {showNotification && (
        <div className={`fixed top-4 right-4 p-3 rounded-md shadow-lg transition-opacity duration-300 ${isDemoMode ? 'bg-green-100 text-green-800 border border-green-200' : 'bg-red-100 text-red-800 border border-red-200'}`}>
          <div className="flex items-center">
            <i className={`fas ${isDemoMode ? 'fa-flask' : 'fa-code'} mr-2`}></i>
            <span className="font-medium">{notificationMessage}</span>
          </div>
        </div>
      )}
      {isExpanded ? (
        <div className="bg-white rounded-lg shadow-lg border border-gray-200 w-96 max-h-[80vh] overflow-hidden flex flex-col">
          <div className="flex justify-between items-center p-4 border-b border-gray-200">
            <h3 className="font-bold text-gray-800">Development Tools</h3>
            <button
              onClick={() => setIsExpanded(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <i className="fas fa-times"></i>
            </button>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-gray-200">
            <button
              className={`flex-1 py-2 px-4 text-sm font-medium ${activeTab === 'demo' ? 'text-blue-600 border-b-2 border-blue-500' : 'text-gray-500 hover:text-gray-700'}`}
              onClick={() => setActiveTab('demo')}
            >
              Demo Mode
            </button>
            <button
              className={`flex-1 py-2 px-4 text-sm font-medium ${activeTab === 'features' ? 'text-blue-600 border-b-2 border-blue-500' : 'text-gray-500 hover:text-gray-700'}`}
              onClick={() => setActiveTab('features')}
            >
              Features
            </button>
            <button
              className={`flex-1 py-2 px-4 text-sm font-medium ${activeTab === 'debug' ? 'text-blue-600 border-b-2 border-blue-500' : 'text-gray-500 hover:text-gray-700'}`}
              onClick={() => setActiveTab('debug')}
            >
              Debug
            </button>
          </div>

          <div className="p-4 overflow-y-auto flex-grow">
            {/* Demo Mode Tab */}
            {activeTab === 'demo' && (
              <div>
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <label className="font-medium text-gray-700">Demo Mode</label>
                    <div className="relative inline-block w-12 align-middle select-none">
                      <input
                        type="checkbox"
                        name="toggle"
                        id="toggle-demo"
                        className="sr-only"
                        checked={isDemoMode}
                        onChange={handleToggleDemoMode}
                      />
                      <label
                        htmlFor="toggle-demo"
                        className={`block overflow-hidden h-6 rounded-full cursor-pointer ${
                          isDemoMode ? 'bg-blue-500' : 'bg-gray-300'
                        }`}
                      >
                        <span
                          className={`block h-6 w-6 rounded-full bg-white transform transition-transform ${
                            isDemoMode ? 'translate-x-6' : 'translate-x-0'
                          }`}
                        ></span>
                      </label>
                    </div>
                  </div>
                  <div className={`p-2 rounded mb-4 ${isDemoMode ? 'bg-blue-50 border border-blue-100' : 'bg-gray-50 border border-gray-100'}`}>
                    <div className="flex items-center">
                      <i className={`fas ${isDemoMode ? 'fa-flask text-blue-500' : 'fa-server text-gray-500'} mr-2`}></i>
                      <div>
                        <p className="text-sm font-medium">
                          {isDemoMode ? 'Demo Mode Active' : 'Production Mode Active'}
                        </p>
                        <p className="text-xs text-gray-500">
                          {isDemoMode
                            ? 'Using mock data and simulated backend'
                            : 'Using real backend and API calls'}
                        </p>
                      </div>
                    </div>
                  </div>

                  {isDemoMode && (
                    <div className="mt-4">
                      <button
                        onClick={resetDemo}
                        className="w-full py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                      >
                        <i className="fas fa-redo mr-2"></i> Reset Demo Data
                      </button>
                      <p className="text-xs text-gray-500 mt-1">
                        Resets the demo workflow to its initial state
                      </p>
                    </div>
                  )}
                </div>

                <div className="mt-6">
                  <h4 className="font-medium text-gray-700 mb-2">Demo Mode Status</h4>
                  <div className="bg-gray-100 p-3 rounded text-sm">
                    <div className="flex justify-between mb-1">
                      <span className="text-gray-600">Status:</span>
                      <span className={isDemoMode ? 'text-green-600 font-medium' : 'text-gray-600'}>
                        {isDemoMode ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    <div className="flex justify-between mb-1">
                      <span className="text-gray-600">Environment:</span>
                      <span className="text-gray-600">
                        {isDevelopment ? 'Development' : 'Production'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Features Tab */}
            {activeTab === 'features' && (
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Feature Flags</h4>
                <div className="space-y-3">
                  {Object.entries(FEATURES).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between">
                      <label className="text-sm text-gray-700">{key}</label>
                      <div className="relative inline-block w-10 align-middle select-none">
                        <input
                          type="checkbox"
                          id={`feature-${key}`}
                          className="sr-only"
                          checked={value === true}
                          onChange={() => {
                            // This is just for display - doesn't actually change the features
                            // In a real implementation, you would update the feature flags
                            console.log(`Toggle feature ${key}: ${!value}`);
                          }}
                          disabled
                        />
                        <label
                          htmlFor={`feature-${key}`}
                          className={`block overflow-hidden h-5 rounded-full cursor-not-allowed ${
                            value === true ? 'bg-blue-500' : 'bg-gray-300'
                          }`}
                        >
                          <span
                            className={`block h-5 w-5 rounded-full bg-white transform transition-transform ${
                              value === true ? 'translate-x-5' : 'translate-x-0'
                            }`}
                          ></span>
                        </label>
                      </div>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Feature flags are read-only in this version
                </p>
              </div>
            )}

            {/* Debug Tab */}
            {activeTab === 'debug' && (
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Debug Tools</h4>

                <div className="space-y-2">
                  <button
                    onClick={() => {
                      console.clear();
                      console.log('Console cleared');
                    }}
                    className="w-full py-2 px-4 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm"
                  >
                    <i className="fas fa-eraser mr-2"></i> Clear Console
                  </button>

                  <button
                    onClick={() => {
                      console.log('Current state:', {
                        isDemoMode,
                        isDevelopment,
                        features: FEATURES,
                        localStorage: {
                          force_dev_tools: localStorage.getItem('force_dev_tools')
                        }
                      });
                    }}
                    className="w-full py-2 px-4 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm"
                  >
                    <i className="fas fa-info-circle mr-2"></i> Log Debug Info
                  </button>
                </div>

                <div className="mt-4">
                  <h4 className="font-medium text-gray-700 mb-2">LocalStorage State</h4>
                  <div className="bg-gray-100 p-3 rounded text-sm mb-4">
                    <div className="flex justify-between mb-1">
                      <span className="text-gray-600">demo_mode_enabled:</span>
                      <span className="font-mono">{localStorage.getItem('demo_mode_enabled') || 'null'}</span>
                    </div>
                    <div className="flex justify-between mb-1">
                      <span className="text-gray-600">force_dev_tools:</span>
                      <span className="font-mono">{localStorage.getItem('force_dev_tools') || 'null'}</span>
                    </div>
                    <button
                      onClick={() => {
                        localStorage.removeItem('demo_mode_enabled');
                        alert('Demo mode preference has been reset. Refresh the page to see changes.');
                      }}
                      className="mt-2 w-full py-1 px-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 text-xs"
                    >
                      <i className="fas fa-trash mr-1"></i> Reset Demo Mode Preference
                    </button>
                  </div>

                  <h4 className="font-medium text-gray-700 mb-2">Visibility Settings</h4>
                  <div className="space-y-2">
                    <button
                      onClick={() => {
                        localStorage.setItem('force_dev_tools', 'true');
                        alert('Development tools will now be visible in production builds');
                      }}
                      className="w-full py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                    >
                      <i className="fas fa-eye mr-2"></i> Force Show in Production
                    </button>
                    <button
                      onClick={() => {
                        localStorage.removeItem('force_dev_tools');
                        alert('Development tools will be hidden in production builds');
                      }}
                      className="w-full py-2 px-4 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                    >
                      <i className="fas fa-eye-slash mr-2"></i> Reset Visibility
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="flex flex-col space-y-2">
          {/* Quick toggle button */}
          <button
            onClick={handleToggleDemoMode}
            className={`p-3 rounded-full shadow-lg transition-colors ${isDemoMode ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'}`}
            title={`Quick Toggle: ${isDemoMode ? 'Disable' : 'Enable'} Demo Mode`}
          >
            <i className="fas fa-power-off"></i>
          </button>

          {/* Settings button */}
          <button
            onClick={() => setIsExpanded(true)}
            className={`p-3 rounded-full shadow-lg transition-colors ${isDemoMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-800 hover:bg-gray-700'}`}
            title="Development Tools"
          >
            <i className={`fas ${isDemoMode ? 'fa-flask' : 'fa-tools'}`}></i>
          </button>
        </div>
      )}
    </div>
  );
};

export default DevelopmentModeToggle;
