// This script checks if we're running in a deployed environment
// and forces demo mode if we are

// Check if we're running on GitHub Pages or another deployment platform
const isDeployed =
  window.location.hostname.includes('github.io') ||
  window.location.hostname.includes('netlify.app') ||
  window.location.hostname.includes('vercel.app') ||
  window.location.hostname.includes('demo') ||
  window.location.search.includes('demo=true');

// Force demo mode if we're deployed
if (isDeployed) {
  console.log('Running in deployed environment - forcing demo mode');
  window.FORCE_DEMO_MODE = true;
  window.STANDALONE_DEMO = true;
  window.ENSURE_DEMO_MODE_PROVIDER = true;

  // Create a global DemoModeContext for components that try to use it
  window.DemoModeContext = {
    isDemoMode: true,
    demoNodes: [],
    demoConnections: [],
    demoPlugins: [],
    updateDemoNodes: function() {},
    updateDemoConnections: function() {},
    executeDemoWorkflow: async function() { return {}; },
    isExecuting: false,
    executionResults: null,
    toggleDemoMode: function() {},
    resetDemo: function() {}
  };

  // Add a banner to indicate demo mode
  window.addEventListener('DOMContentLoaded', () => {
    const banner = document.createElement('div');
    banner.style.backgroundColor = '#f0f9ff';
    banner.style.padding = '10px';
    banner.style.textAlign = 'center';
    banner.style.borderBottom = '1px solid #bae6fd';
    banner.style.position = 'fixed';
    banner.style.top = '0';
    banner.style.left = '0';
    banner.style.right = '0';
    banner.style.zIndex = '9999';

    banner.innerHTML = `
      <p style="margin: 0; font-size: 14px;">
        <strong>Workflow Builder Demo</strong> - This is a demo that runs entirely in your browser. No installation required!
        <a href="https://github.com/Sagura091/workflow-builder" target="_blank" style="color: #0284c7; text-decoration: underline; margin-left: 10px;">View on GitHub</a>
      </p>
    `;

    document.body.prepend(banner);

    // Add some padding to the top of the page to account for the banner
    const root = document.getElementById('root');
    if (root) {
      root.style.paddingTop = '40px';
    }
  });

  // Add error handling for React errors
  window.addEventListener('error', function(event) {
    if (event.error && event.error.message && event.error.message.includes('DemoModeProvider')) {
      console.warn('Caught DemoModeProvider error, reloading page...');
      // Reload the page after a short delay
      setTimeout(function() {
        window.location.reload();
      }, 1000);
    }
  });
}
