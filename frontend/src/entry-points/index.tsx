import React from 'react';
import ReactDOM from 'react-dom/client';
import '../styles/index.css';
import App from '../pages/App';
import DemoApp from '../pages/DemoApp';
import reportWebVitals from '../utils/reportWebVitals';

// Check if we're in demo mode
const isDemoMode = process.env.REACT_APP_DEMO_MODE === 'true' ||
                  window.location.search.includes('demo=true') ||
                  window.location.hostname.includes('demo') ||
                  window.location.hostname === 'localhost' ||
                  (window as any).FORCE_DEMO_MODE === true;

// Check if we need to ensure DemoModeProvider is available
const ensureDemoModeProvider = (window as any).ENSURE_DEMO_MODE_PROVIDER === true;

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    {isDemoMode ? <DemoApp /> : <App />}
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
