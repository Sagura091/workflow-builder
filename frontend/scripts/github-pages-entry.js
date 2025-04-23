// GitHub Pages Entry Point (JavaScript version)
import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/index.css';
import DemoApp from './pages/DemoApp';
import { DemoModeProvider } from './contexts/DemoModeContext';

// Force demo mode for GitHub Pages
var win = window;
win.FORCE_DEMO_MODE = true;
win.STANDALONE_DEMO = true;
win.ENSURE_DEMO_MODE_PROVIDER = true;

// Disable features that require a backend
if (typeof window !== 'undefined') {
  if (win.FEATURES) {
    win.FEATURES = {
      ...win.FEATURES,
      WEBSOCKETS_ENABLED: false,
      ENABLE_SCHEDULING: false
    };
  } else {
    // If FEATURES doesn't exist yet, create it
    win.FEATURES = {
      WEBSOCKETS_ENABLED: false,
      ENABLE_SCHEDULING: false,
      NODE_INSTANCES_ENABLED: true,
      LAZY_LOADING_ENABLED: true,
      ENABLE_TEMPLATES: true,
      ENABLE_CACHING: true,
      ENABLE_PARTIAL_EXECUTION: true,
      ENABLE_TYPE_VALIDATION: true,
      ENABLE_DARK_MODE: true
    };
  }
}

// Log that we're using the GitHub Pages entry point
console.log('Using GitHub Pages entry point');
console.log('Demo mode enabled: standalone demo with no backend requirements');

const root = ReactDOM.createRoot(document.getElementById('root'));

// Render the app with DemoModeProvider explicitly wrapped around it
root.render(
  React.createElement(
    React.StrictMode,
    null,
    React.createElement(
      DemoModeProvider,
      null,
      React.createElement(DemoApp, null)
    )
  )
);
