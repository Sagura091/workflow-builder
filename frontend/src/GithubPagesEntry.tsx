import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import DemoApp from './DemoApp';
import { DemoModeProvider } from './contexts/DemoModeContext';

// Force demo mode for GitHub Pages
window.FORCE_DEMO_MODE = true;
window.STANDALONE_DEMO = true;
window.ENSURE_DEMO_MODE_PROVIDER = true;

// Log that we're using the GitHub Pages entry point
console.log('Using GitHub Pages entry point');

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

// Render the app with DemoModeProvider explicitly wrapped around it
root.render(
  <React.StrictMode>
    <DemoModeProvider>
      <DemoApp />
    </DemoModeProvider>
  </React.StrictMode>
);
