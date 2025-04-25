/**
 * Development Tools
 * 
 * This file contains utility functions for development purposes.
 * These functions can be called from the browser console.
 */

// Make the functions available globally
window.devTools = {
  /**
   * Toggle demo mode
   * @param {boolean} [force] - Force demo mode on or off
   * @returns {boolean} The new demo mode state
   */
  toggleDemoMode: (force) => {
    // Find the demo mode context
    const demoModeContext = window.__DEMO_MODE_CONTEXT__;
    
    if (!demoModeContext) {
      console.error('Demo mode context not found');
      return false;
    }
    
    if (typeof force === 'boolean') {
      // Force demo mode on or off
      if (force !== demoModeContext.isDemoMode) {
        demoModeContext.toggleDemoMode();
      }
      console.log(`Demo mode ${force ? 'enabled' : 'disabled'}`);
      return force;
    } else {
      // Toggle demo mode
      demoModeContext.toggleDemoMode();
      console.log(`Demo mode ${demoModeContext.isDemoMode ? 'enabled' : 'disabled'}`);
      return demoModeContext.isDemoMode;
    }
  },
  
  /**
   * Enable demo mode
   * @returns {boolean} The new demo mode state
   */
  enableDemoMode: () => {
    return window.devTools.toggleDemoMode(true);
  },
  
  /**
   * Disable demo mode
   * @returns {boolean} The new demo mode state
   */
  disableDemoMode: () => {
    return window.devTools.toggleDemoMode(false);
  },
  
  /**
   * Show development tools in production
   */
  showDevTools: () => {
    localStorage.setItem('force_dev_tools', 'true');
    console.log('Development tools will now be visible in production builds');
    console.log('Refresh the page to see the changes');
  },
  
  /**
   * Hide development tools in production
   */
  hideDevTools: () => {
    localStorage.removeItem('force_dev_tools');
    console.log('Development tools will be hidden in production builds');
    console.log('Refresh the page to see the changes');
  }
};

// Log available commands
console.log(
  '%c Development Tools Available ',
  'background: #2563eb; color: white; padding: 2px 4px; border-radius: 4px; font-weight: bold;'
);
console.log(
  '%c Call these functions from the console: ',
  'font-weight: bold;'
);
console.log(
  '- devTools.toggleDemoMode() - Toggle demo mode\n' +
  '- devTools.enableDemoMode() - Enable demo mode\n' +
  '- devTools.disableDemoMode() - Disable demo mode\n' +
  '- devTools.showDevTools() - Show development tools in production\n' +
  '- devTools.hideDevTools() - Hide development tools in production'
);

// Export for module usage
export const devTools = window.devTools;
