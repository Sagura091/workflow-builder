import React from 'react';
import { useDemoMode } from '../../contexts/DemoModeContext';

const DemoModeToggle: React.FC = () => {
  const { isDemoMode, toggleDemoMode, resetDemo } = useDemoMode();

  return (
    <div className="fixed top-4 right-4 z-50 flex items-center space-x-2">
      <div className="bg-white rounded-lg shadow-md p-2 flex items-center space-x-3">
        <div className="flex items-center">
          <label htmlFor="demo-toggle" className="mr-2 text-sm font-medium text-gray-700">
            Demo Mode
          </label>
          <div className="relative inline-block w-12 h-6 transition duration-200 ease-in-out rounded-full">
            <input
              id="demo-toggle"
              type="checkbox"
              className="absolute w-6 h-6 transition duration-200 ease-in-out transform bg-white border-2 rounded-full appearance-none cursor-pointer border-gray-300 checked:translate-x-6 checked:border-blue-500 peer"
              checked={isDemoMode}
              onChange={toggleDemoMode}
            />
            <label
              htmlFor="demo-toggle"
              className="block w-full h-full rounded-full cursor-pointer bg-gray-300 peer-checked:bg-blue-500"
            ></label>
          </div>
        </div>
        
        {isDemoMode && (
          <button
            className="px-2 py-1 text-xs text-white bg-blue-500 rounded hover:bg-blue-600"
            onClick={resetDemo}
          >
            Reset Demo
          </button>
        )}
      </div>
      
      {isDemoMode && (
        <div className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-xs font-medium animate-pulse">
          Demo Mode Active
        </div>
      )}
    </div>
  );
};

export default DemoModeToggle;
