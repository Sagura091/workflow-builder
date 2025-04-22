import React, { useState } from 'react';
import { Workflow } from '../../types';
import TemplateGallery from './TemplateGallery';

interface WorkflowHeaderProps {
  workflowName: string;
  onNewWorkflow: () => void;
  onClearCanvas: () => void;
  onLoadTemplate?: (workflow: Workflow) => void;
  onShowShortcuts?: () => void;
}

const WorkflowHeader: React.FC<WorkflowHeaderProps> = ({
  workflowName,
  onNewWorkflow,
  onClearCanvas,
  onLoadTemplate,
  onShowShortcuts
}) => {
  const [showTemplateGallery, setShowTemplateGallery] = useState(false);
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">ML Workflows</h1>
          <p className="text-gray-600 mt-1">Design, manage and execute machine learning pipelines</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={onNewWorkflow}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition"
          >
            <i className="fas fa-plus mr-2"></i> New Workflow
          </button>
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            <i className="fas fa-file-import mr-2"></i> Import
          </button>
          <button
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
            onClick={() => setShowTemplateGallery(true)}
          >
            <i className="fas fa-shapes mr-2"></i> Templates
          </button>
          <button
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition"
            onClick={() => onShowShortcuts && onShowShortcuts()}
          >
            <i className="fas fa-keyboard mr-2"></i> Shortcuts
          </button>
          <button
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 transition"
          >
            <i className="fas fa-folder-open mr-2"></i> Load
          </button>
        </div>
      </div>

      {/* Template Gallery */}
      {showTemplateGallery && (
        <TemplateGallery
          onSelectTemplate={(templateWorkflow) => {
            if (onLoadTemplate) {
              onLoadTemplate(templateWorkflow);
            }
            setShowTemplateGallery(false);
          }}
          onClose={() => setShowTemplateGallery(false)}
        />
      )}
    </div>
  );
};

export default WorkflowHeader;
