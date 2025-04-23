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

  // Add a banner and welcome message to indicate demo mode
  window.addEventListener('DOMContentLoaded', () => {
    // Create the banner
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
        <strong>Workflow Builder Demo</strong> - This is a fully interactive demo that runs entirely in your browser. No installation required!
        <a href="https://github.com/Sagura091/workflow-builder" target="_blank" style="color: #0284c7; text-decoration: underline; margin-left: 10px;">View on GitHub</a>
        <button id="demo-help-btn" style="margin-left: 10px; background-color: #0284c7; color: white; border: none; border-radius: 4px; padding: 2px 8px; cursor: pointer;">How to Use</button>
      </p>
    `;

    document.body.prepend(banner);

    // Add some padding to the top of the page to account for the banner
    const root = document.getElementById('root');
    if (root) {
      root.style.paddingTop = '40px';
    }

    // Add event listener for the help button
    setTimeout(() => {
      const helpBtn = document.getElementById('demo-help-btn');
      if (helpBtn) {
        helpBtn.addEventListener('click', showHelpModal);
      }

      // Show welcome message after a short delay
      setTimeout(showWelcomeMessage, 1000);
    }, 500);
  });

  // Function to show the welcome message
  function showWelcomeMessage() {
    alert('Welcome to the Workflow Builder Demo!\n\n' +
          'This is a fully interactive demo that runs entirely in your browser.\n\n' +
          'You can:\n' +
          '- Drag nodes from the left panel to the canvas\n' +
          '- Connect nodes by dragging from output to input ports\n' +
          '- Configure nodes by clicking on them\n' +
          '- Execute the workflow to see it in action\n\n' +
          'Click the "How to Use" button in the top banner for more details.');
  }

  // Function to show the help modal
  function showHelpModal() {
    alert('How to Use the Workflow Builder Demo:\n\n' +
          '1. Drag and Drop: Drag nodes from the left panel to the canvas\n' +
          '2. Connect Nodes: Click and drag from an output port (right side of node) to an input port (left side of node)\n' +
          '3. Configure Nodes: Click on a node to select it and edit its properties in the right panel\n' +
          '4. Execute Workflow: Click the Execute button to run the workflow\n' +
          '5. Zoom: Use the mouse wheel to zoom in/out\n' +
          '6. Pan: Hold the middle mouse button or Alt+left-click and drag to pan the canvas\n' +
          '7. Center View: Press "C" to center the view\n\n' +
          'Note: This is a demo version that simulates workflow execution in the browser. In a real implementation, this would connect to a backend service.');
  }

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
