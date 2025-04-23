// Global type declarations for the application

interface Window {
  FORCE_DEMO_MODE?: boolean;
  STANDALONE_DEMO?: boolean;
  ENSURE_DEMO_MODE_PROVIDER?: boolean;
  DemoModeContext?: any;
}

// Extend the global Window interface
declare global {
  interface Window {
    FORCE_DEMO_MODE?: boolean;
    STANDALONE_DEMO?: boolean;
    ENSURE_DEMO_MODE_PROVIDER?: boolean;
    DemoModeContext?: any;
  }
}
