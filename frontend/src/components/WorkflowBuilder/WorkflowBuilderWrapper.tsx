import React from 'react';
import { DemoModeProvider } from '../../contexts/DemoModeContext';
import WorkflowBuilder from './index';

const WorkflowBuilderWrapper: React.FC = () => {
  // Check if we're already inside a DemoModeProvider
  // This prevents nesting DemoModeProviders which can cause issues
  const isStandalone = (window as any).STANDALONE_DEMO === true;
  const isDemoMode = (window as any).FORCE_DEMO_MODE === true;

  // In DemoApp.tsx, we're already wrapped in a DemoModeProvider
  // So we only need to add one here if we're not in demo mode
  if (isStandalone || isDemoMode) {
    return <WorkflowBuilder />;
  }

  return (
    <DemoModeProvider>
      <WorkflowBuilder />
    </DemoModeProvider>
  );
};

export default WorkflowBuilderWrapper;
