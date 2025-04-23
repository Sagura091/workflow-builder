const fs = require('fs');
const path = require('path');

console.log('Restoring original index.js...');

// Paths
const srcDir = path.resolve(__dirname, '../src');
const originalIndexPath = path.resolve(srcDir, 'index.js.original');
const indexPath = path.resolve(srcDir, 'index.js');

// Check if the original index.js exists
if (fs.existsSync(originalIndexPath)) {
  // Restore the original index.js
  fs.copyFileSync(originalIndexPath, indexPath);
  fs.unlinkSync(originalIndexPath);
  console.log('Original index.js restored successfully.');
} else {
  // Create a default index.js if the original doesn't exist
  const defaultIndexContent = `import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/index.css';
import App from './pages/App';
import reportWebVitals from './utils/reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
`;

  fs.writeFileSync(indexPath, defaultIndexContent);
  console.log('Default index.js created successfully.');
}
