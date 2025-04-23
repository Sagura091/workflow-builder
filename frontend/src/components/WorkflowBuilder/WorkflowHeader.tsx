import React, { useState, useRef } from 'react';
import { Workflow } from '../../types';
import TemplateGallery from './TemplateGallery';

interface WorkflowHeaderProps {
  workflowName: string;
  onNewWorkflow: () => void;
  onClearCanvas: () => void;
  onSaveWorkflow?: () => void;
  onLoadWorkflow?: () => void;
  onImportWorkflow?: (workflow: Workflow) => void;
  onExportWorkflow?: () => void;
  onLoadTemplate?: (workflow: Workflow) => void;
  onShowShortcuts?: () => void;
}

const WorkflowHeader: React.FC<WorkflowHeaderProps> = ({
  workflowName,
  onNewWorkflow,
  onClearCanvas,
  onSaveWorkflow,
  onLoadWorkflow,
  onImportWorkflow,
  onExportWorkflow,
  onLoadTemplate,
  onShowShortcuts
}) => {
  const [showTemplateGallery, setShowTemplateGallery] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
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
            title="Create a new workflow (Ctrl+N)"
          >
            <i className="fas fa-plus mr-2"></i> New
          </button>
          <button
            onClick={() => {
              if (onSaveWorkflow) onSaveWorkflow();
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
            title="Save the current workflow (Ctrl+S)"
          >
            <i className="fas fa-save mr-2"></i> Save
          </button>
          <button
            onClick={() => {
              if (onLoadWorkflow) onLoadWorkflow();
            }}
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 transition"
            title="Load a saved workflow (Ctrl+O)"
          >
            <i className="fas fa-folder-open mr-2"></i> Load
          </button>
          <button
            onClick={() => {
              if (fileInputRef.current) fileInputRef.current.click();
            }}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
            title="Import a workflow from a file (Ctrl+I)"
          >
            <i className="fas fa-file-import mr-2"></i> Import
          </button>
          <button
            onClick={() => {
              if (onExportWorkflow) onExportWorkflow();
            }}
            className="px-4 py-2 bg-teal-600 text-white rounded hover:bg-teal-700 transition"
            title="Export the current workflow to a file (Ctrl+E)"
          >
            <i className="fas fa-file-export mr-2"></i> Export
          </button>
          <button
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
            onClick={() => setShowTemplateGallery(true)}
            title="Choose from pre-built workflow templates (Ctrl+T)"
          >
            <i className="fas fa-shapes mr-2"></i> Templates
          </button>
          <button
            onClick={onClearCanvas}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
            title="Clear the canvas (Ctrl+Delete)"
          >
            <i className="fas fa-trash mr-2"></i> Clear
          </button>
          <button
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition"
            onClick={() => onShowShortcuts && onShowShortcuts()}
            title="View keyboard shortcuts (F1)"
          >
            <i className="fas fa-keyboard mr-2"></i> Shortcuts
          </button>

          {/* Hidden file input for importing */}
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: 'none' }}
            accept=".json"
            onChange={(e) => {
              if (e.target.files && e.target.files[0] && onImportWorkflow) {
                const file = e.target.files[0];
                const reader = new FileReader();
                reader.onload = (event) => {
                  try {
                    if (event.target && typeof event.target.result === 'string') {
                      const workflow = JSON.parse(event.target.result);
                      onImportWorkflow(workflow);
                    }
                  } catch (error) {
                    console.error('Error parsing workflow file:', error);
                    alert('Error importing workflow: Invalid file format');
                  }
                };
                reader.readAsText(file);
                // Reset the input so the same file can be selected again
                e.target.value = '';
              }
            }}
          />
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
