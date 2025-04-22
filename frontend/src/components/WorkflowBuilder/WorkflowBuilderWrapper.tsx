import React from 'react';
import { DemoModeProvider } from '../../contexts/DemoModeContext';
import WorkflowBuilder from './index';

const WorkflowBuilderWrapper: React.FC = () => {
  return (
    <DemoModeProvider>
      <WorkflowBuilder />
    </DemoModeProvider>
  );
};

export default WorkflowBuilderWrapper;
