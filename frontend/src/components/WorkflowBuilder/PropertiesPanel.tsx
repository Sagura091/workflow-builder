import React, { useState, useEffect, useRef } from 'react';
import { NodeData, Plugin, ConfigField } from '../../types';
import { useNodeTypes } from '../../contexts/NodeTypesContext';
import { TYPE_COLORS } from '../../config';
import { CodeEditor, JsonEditor, ColorPicker } from '../../components/FormControls';
import './PropertiesPanel.css';

interface PropertiesPanelProps {
  selectedNode: NodeData | undefined;
  plugins: Plugin[];
  onUpdateConfig: (nodeId: string, config: Record<string, any>) => void;
}

const PropertiesPanel: React.FC<PropertiesPanelProps> = ({
  selectedNode,
  plugins,
  onUpdateConfig
}) => {
  // Call hooks at the top level
  const nodeTypesContext = useNodeTypes();
  const [config, setConfig] = useState<Record<string, any>>({});
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    'general': true,
    'inputs': false,
    'outputs': false,
    'config': true,
    'preview': false,
    'validation': false
  });

  // State for validation results
  const [validationResults, setValidationResults] = useState<{valid: boolean, errors: string[]}>({valid: true, errors: []});

  // State for preview data
  const [previewData, setPreviewData] = useState<any>(null);

  // Ref for the form
  const formRef = useRef<HTMLFormElement>(null);

  // Initialize form with node config
  useEffect(() => {
    if (selectedNode) {
      setConfig(selectedNode.config || {});
    } else {
      setConfig({});
    }
  }, [selectedNode]);

  if (!selectedNode) {
    return (
      <div className="properties-panel bg-white border-l border-gray-200 p-4 w-full h-full overflow-y-auto rounded-lg shadow-md">
        <div className="text-center text-gray-500 py-8">
          <i className="fas fa-arrow-left text-2xl mb-2"></i>
          <p>Select a node to view and edit its properties</p>
          <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-100 text-sm text-blue-800">
            <h3 className="font-medium mb-2">Tips:</h3>
            <ul className="list-disc pl-5 space-y-1">
              <li>Click on any node in the canvas to edit its properties</li>
              <li>Use the mouse wheel to zoom in/out</li>
              <li>Hold middle mouse button or Alt+Left click to pan the canvas</li>
              <li>Drag from output to input points to create connections</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  // Get node type information
  const getNodeTypeInfo = (type: string) => {
    if (!type) {
      return { title: 'Unknown', configFields: [] };
    }

    // First check built-in node types
    const builtInTypes: Record<string, { title: string, configFields: ConfigField[] }> = {
      data_loader: {
        title: "Data Loader",
        configFields: [
          { name: "data_source", label: "Data Source", type: "text", placeholder: "Enter data source path or URL" },
          { name: "format", label: "Format", type: "select", options: ["CSV", "JSON", "Parquet", "SQL"] },
          { name: "connection_color", label: "Connection Color", type: "color" }
        ]
      },
      data_transform: {
        title: "Data Transform",
        configFields: [
          { name: "transform_type", label: "Transform Type", type: "select", options: ["Normalize", "Standardize", "One-Hot Encode", "Missing Values"] },
          { name: "params", label: "Parameters", type: "textarea", placeholder: "Transform parameters in JSON format" }
        ]
      },
      feature_engineering: {
        title: "Feature Engineering",
        configFields: [
          { name: "feature_methods", label: "Feature Methods", type: "select", multiple: true, options: ["PCA", "Feature Selection", "Aggregation", "Custom"] },
          { name: "settings", label: "Settings", type: "json", placeholder: "{\n  \"method\": \"pca\",\n  \"n_components\": 5\n}" }
        ]
      },
      train_model: {
        title: "Train Model",
        configFields: [
          { name: "model_type", label: "Model Type", type: "select", options: ["Linear", "Random Forest", "Neural Network", "SVM", "Custom"] },
          { name: "hyperparams", label: "Hyperparameters", type: "json", placeholder: "{\n  \"learning_rate\": 0.01,\n  \"max_depth\": 5\n}" },
          { name: "custom_code", label: "Custom Code", type: "code", language: "python", height: "150px", placeholder: "# Custom model code\ndef train_model(X, y):\n    # Your code here\n    return model" },
          { name: "validation", label: "Use Validation", type: "checkbox" }
        ]
      },
      evaluate: {
        title: "Evaluate",
        configFields: [
          { name: "metrics", label: "Metrics", type: "select", multiple: true, options: ["Accuracy", "Precision", "Recall", "F1", "ROC AUC", "MSE"] }
        ]
      },
      predict: {
        title: "Predict",
        configFields: [
          { name: "output_format", label: "Output Format", type: "select", options: ["JSON", "CSV", "Database"] },
          { name: "batch_size", label: "Batch Size", type: "number", min: 1, step: 10 }
        ]
      },
      deploy_model: {
        title: "Deploy Model",
        configFields: [
          { name: "service_name", label: "Service Name", type: "text" },
          { name: "replicas", label: "Replicas", type: "number", min: 1 },
          { name: "environment", label: "Environment", type: "select", options: ["Development", "Staging", "Production"] }
        ]
      },
      monitoring: {
        title: "Monitoring",
        configFields: [
          { name: "alert_threshold", label: "Alert Threshold", type: "number" },
          { name: "metrics", label: "Metrics to Monitor", type: "select", multiple: true, options: ["Drift", "Latency", "Error Rate", "Usage"] }
        ]
      }
    };

    // Check if it's a built-in type
    if (builtInTypes[type]) {
      return builtInTypes[type];
    }

    // Check if it's a plugin
    const plugin = plugins.find(p => p.id === type);
    if (plugin && plugin.__plugin_meta__) {
      return {
        title: plugin.__plugin_meta__.name || 'Plugin',
        configFields: plugin.__plugin_meta__.configFields || []
      };
    }

    // Default
    return { title: type, configFields: [] };
  };

  // Get node types from context
  const nodeTypes: Record<string, { inputs: Array<{id: string, name: string, type: string, ui_properties?: any}>, outputs: Array<{id: string, name: string, type: string, ui_properties?: any}> }> =
    (nodeTypesContext?.nodeTypes as Record<string, { inputs: Array<{id: string, name: string, type: string, ui_properties?: any}>, outputs: Array<{id: string, name: string, type: string, ui_properties?: any}> }>) || {};

  // Get node inputs and outputs
  const getNodePorts = (type: string) => {
    if (!type) {
      return { inputs: [], outputs: [] };
    }

    // First try to get from the context
    if (nodeTypes && nodeTypes[type]) {
      return nodeTypes[type];
    }

    // Fallback to hardcoded values if not found in context
    const nodePorts: Record<string, { inputs: Array<{id: string, name: string, type: string, ui_properties?: any}>, outputs: Array<{id: string, name: string, type: string, ui_properties?: any}> }> = {
      'core.begin': {
        inputs: [],
        outputs: [
          { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'right-top' } },
          { id: 'workflow_id', name: 'Workflow ID', type: 'string', ui_properties: { position: 'right-center' } },
          { id: 'timestamp', name: 'Timestamp', type: 'number', ui_properties: { position: 'right-bottom' } }
        ]
      },
      'core.end': {
        inputs: [
          { id: 'trigger', name: 'Trigger', type: 'trigger', ui_properties: { position: 'left-top' } },
          { id: 'result', name: 'Result', type: 'any', ui_properties: { position: 'left-center' } }
        ],
        outputs: [
          { id: 'workflow_id', name: 'Workflow ID', type: 'string', ui_properties: { position: 'right-top' } },
          { id: 'execution_time', name: 'Execution Time', type: 'number', ui_properties: { position: 'right-center' } }
        ]
      }
    };

    return nodePorts[type] || { inputs: [], outputs: [] };
  };

  const { title, configFields } = getNodeTypeInfo(selectedNode?.type || '');
  const { inputs, outputs } = getNodePorts(selectedNode?.type || '');

  // Handle form field change
  const handleFieldChange = (name: string, value: any) => {
    const newConfig = {
      ...config,
      [name]: value
    };

    setConfig(newConfig);

    // Validate the field
    validateField(name, value);

    // Update the node config in real-time
    if (selectedNode?.id) {
      onUpdateConfig(selectedNode.id, newConfig);
    }
  };

  // Validate a single field
  const validateField = (name: string, value: any) => {
    // Find the field definition
    const field = configFields.find(f => f.name === name);
    if (!field) return;

    // Basic validation
    let isValid = true;
    let errorMessage = '';

    if (field.type === 'number') {
      if (field.min !== undefined && value < field.min) {
        isValid = false;
        errorMessage = `Value must be at least ${field.min}`;
      }
    } else if (field.type === 'text' || field.type === 'textarea') {
      if (value === '' && field.placeholder?.includes('required')) {
        isValid = false;
        errorMessage = 'This field is required';
      }
    }

    // Update validation results
    setValidationResults(prev => {
      const errors = [...prev.errors];
      const errorIndex = errors.findIndex(e => e.startsWith(`${name}:`));

      if (!isValid) {
        const errorText = `${name}: ${errorMessage}`;
        if (errorIndex >= 0) {
          errors[errorIndex] = errorText;
        } else {
          errors.push(errorText);
        }
      } else if (errorIndex >= 0) {
        errors.splice(errorIndex, 1);
      }

      return {
        valid: errors.length === 0,
        errors
      };
    });
  };

  // Toggle section expansion
  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Render form field based on type
  const renderField = (field: ConfigField) => {
    const value = config[field.name] !== undefined ? config[field.name] : '';

    switch (field.type) {
      case 'text':
        return (
          <input
            type="text"
            name={field.name}
            value={value as string}
            placeholder={field.placeholder || ''}
            onChange={(e) => handleFieldChange(field.name, e.target.value)}
            className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        );

      case 'number':
        return (
          <input
            type="number"
            name={field.name}
            value={value as number}
            min={field.min || 0}
            step={field.step || 1}
            onChange={(e) => handleFieldChange(field.name, parseFloat(e.target.value))}
            className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        );

      case 'select':
        return field.multiple ? (
          <select
            name={field.name}
            multiple
            value={Array.isArray(value) ? value : []}
            onChange={(e) => {
              const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);
              handleFieldChange(field.name, selectedOptions);
            }}
            className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {field.options?.map((option: string) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        ) : (
          <select
            name={field.name}
            value={value as string}
            onChange={(e) => handleFieldChange(field.name, e.target.value)}
            className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select...</option>
            {field.options?.map((option: string) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        );

      case 'textarea':
        return (
          <textarea
            name={field.name}
            value={value as string}
            placeholder={field.placeholder || ''}
            onChange={(e) => handleFieldChange(field.name, e.target.value)}
            className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
        );

      case 'checkbox':
        return (
          <div className="flex items-center">
            <input
              type="checkbox"
              name={field.name}
              id={`prop-${field.name}`}
              checked={!!value}
              onChange={(e) => handleFieldChange(field.name, e.target.checked)}
              className="h-4 w-4 text-blue-600 rounded"
            />
            <label htmlFor={`prop-${field.name}`} className="ml-2 text-sm text-gray-700">{field.label}</label>
          </div>
        );

      case 'code':
        return (
          <CodeEditor
            value={value as string}
            onChange={(newValue) => handleFieldChange(field.name, newValue)}
            language={field.language || 'javascript'}
            height={field.height || '200px'}
            placeholder={field.placeholder || '// Enter code here'}
            helpText={field.helpText}
          />
        );

      case 'json':
        return (
          <JsonEditor
            value={value}
            onChange={(newValue) => handleFieldChange(field.name, newValue)}
            height={field.height || '200px'}
            placeholder={field.placeholder || '{}'}
            helpText={field.helpText}
            label={field.label}
          />
        );

      case 'color':
        return (
          <ColorPicker
            value={value as string || '#3b82f6'}
            onChange={(newValue) => handleFieldChange(field.name, newValue)}
            helpText={field.helpText}
          />
        );

      default:
        return null;
    }
  };

  // Generate a preview of the node's output
  const generatePreview = () => {
    // This would normally call the backend to get a preview
    // For now, we'll just generate some mock data
    const mockPreview = {
      timestamp: new Date().toISOString(),
      sample: {
        output: selectedNode?.type.includes('text') ? 'Sample text output' :
               selectedNode?.type.includes('number') ? 42 :
               selectedNode?.type.includes('boolean') ? true :
               { data: 'Sample object data' }
      }
    };

    setPreviewData(mockPreview);
    setExpandedSections(prev => ({ ...prev, preview: true }));
  };

  // Reset the form to default values
  const resetForm = () => {
    if (selectedNode) {
      // Get default values from the node type definition
      const defaultConfig: Record<string, any> = {};
      configFields.forEach(field => {
        if (field.name in selectedNode.config) {
          defaultConfig[field.name] = selectedNode.config[field.name];
        } else {
          // Set default values based on field type
          switch (field.type) {
            case 'text':
            case 'textarea':
              defaultConfig[field.name] = '';
              break;
            case 'number':
              defaultConfig[field.name] = field.min || 0;
              break;
            case 'select':
              defaultConfig[field.name] = field.multiple ? [] : '';
              break;
            case 'checkbox':
              defaultConfig[field.name] = false;
              break;
          }
        }
      });

      setConfig(defaultConfig);
      onUpdateConfig(selectedNode.id, defaultConfig);
    }
  };

  return (
    <div className="properties-panel bg-white border-l border-gray-200 p-4 w-full h-full overflow-y-auto rounded-lg shadow-md">
      <form ref={formRef} onSubmit={(e) => e.preventDefault()}>
        {/* Header */}
        <div className="flex justify-between items-center mb-4 pb-2 border-b">
          <h3 className="text-lg font-semibold">{title}</h3>
          <div className="text-xs text-gray-500">ID: {selectedNode?.id || 'N/A'}</div>
        </div>

        {/* Action buttons */}
        <div className="flex justify-between mb-4">
          <button
            type="button"
            className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
            onClick={generatePreview}
          >
            <i className="fas fa-eye mr-1"></i> Preview
          </button>
          <button
            type="button"
            className="px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300 transition-colors"
            onClick={resetForm}
          >
            <i className="fas fa-undo mr-1"></i> Reset
          </button>
        </div>

        {/* Validation errors */}
        {!validationResults.valid && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
            <div className="font-medium mb-1">Please fix the following errors:</div>
            <ul className="list-disc pl-5">
              {validationResults.errors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </div>
        )}

      {/* General section */}
      <div className="mb-4">
        <div
          className="flex justify-between items-center cursor-pointer py-2 border-b"
          onClick={() => toggleSection('general')}
        >
          <h4 className="font-medium text-gray-700">General</h4>
          <i className={`fas fa-chevron-${expandedSections.general ? 'down' : 'right'} text-gray-500`}></i>
        </div>

        {expandedSections.general && (
          <div className="py-2 space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Type</label>
              <div className="text-sm bg-gray-100 p-2 rounded">{selectedNode?.type || 'N/A'}</div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Position</label>
              <div className="text-sm bg-gray-100 p-2 rounded">
                X: {selectedNode ? Math.round(selectedNode.x) : 'N/A'}, Y: {selectedNode ? Math.round(selectedNode.y) : 'N/A'}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Inputs section */}
      <div className="mb-4">
        <div
          className="flex justify-between items-center cursor-pointer py-2 border-b"
          onClick={() => toggleSection('inputs')}
        >
          <h4 className="font-medium text-gray-700">Inputs</h4>
          <div className="flex items-center">
            <span className="text-xs text-gray-500 mr-2">{inputs.length}</span>
            <i className={`fas fa-chevron-${expandedSections.inputs ? 'down' : 'right'} text-gray-500`}></i>
          </div>
        </div>

        {expandedSections.inputs && (
          <div className="py-2">
            {inputs.length > 0 ? (
              <div className="space-y-2">
                {inputs.map(input => (
                  <div key={input.id || input.name} className="flex items-center p-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors">
                    <div className="w-2 h-2 rounded-full bg-blue-500 mr-2"></div>
                    <div className="flex-grow">
                      <div className="text-sm font-medium">{input.name}</div>
                      <div className={`type-indicator ${input.type}`}>{input.type}</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-gray-500 italic">No inputs</div>
            )}
          </div>
        )}
      </div>

      {/* Outputs section */}
      <div className="mb-4">
        <div
          className="flex justify-between items-center cursor-pointer py-2 border-b"
          onClick={() => toggleSection('outputs')}
        >
          <h4 className="font-medium text-gray-700">Outputs</h4>
          <div className="flex items-center">
            <span className="text-xs text-gray-500 mr-2">{outputs.length}</span>
            <i className={`fas fa-chevron-${expandedSections.outputs ? 'down' : 'right'} text-gray-500`}></i>
          </div>
        </div>

        {expandedSections.outputs && (
          <div className="py-2">
            {outputs.length > 0 ? (
              <div className="space-y-2">
                {outputs.map(output => (
                  <div key={output.id || output.name} className="flex items-center justify-between p-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors">
                    <div className="flex-grow">
                      <div className="text-sm font-medium">{output.name}</div>
                      <div className={`type-indicator ${output.type}`}>{output.type}</div>
                    </div>
                    <div className="w-2 h-2 rounded-full bg-green-500 ml-2"></div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-gray-500 italic">No outputs</div>
            )}
          </div>
        )}
      </div>

      {/* Configuration section */}
      <div className="mb-4">
        <div
          className="flex justify-between items-center cursor-pointer py-2 border-b"
          onClick={() => toggleSection('config')}
        >
          <h4 className="font-medium text-gray-700">Configuration</h4>
          <i className={`fas fa-chevron-${expandedSections.config ? 'down' : 'right'} text-gray-500`}></i>
        </div>

        {expandedSections.config && (
          <div className="py-2 space-y-4">
            {configFields.length > 0 ? (
              configFields.map(field => (
                <div key={field.name} className="mb-3">
                  <label className="block text-xs font-medium text-gray-700 mb-1">{field.label}</label>
                  {renderField(field)}
                </div>
              ))
            ) : (
              <div className="text-sm text-gray-500 italic">No configuration options available</div>
            )}
          </div>
        )}
      </div>

      {/* Preview section */}
      <div className="mb-4">
        <div
          className="flex justify-between items-center cursor-pointer py-2 border-b"
          onClick={() => toggleSection('preview')}
        >
          <h4 className="font-medium text-gray-700">Preview</h4>
          <i className={`fas fa-chevron-${expandedSections.preview ? 'down' : 'right'} text-gray-500`}></i>
        </div>

        {expandedSections.preview && (
          <div className="py-2 space-y-3">
            {previewData ? (
              <div>
                <div className="text-xs text-gray-500 mb-1">Generated at: {previewData.timestamp}</div>
                <div className="bg-gray-50 p-3 rounded border border-gray-200 text-sm">
                  <pre className="whitespace-pre-wrap">
                    {JSON.stringify(previewData.sample, null, 2)}
                  </pre>
                </div>
                <div className="mt-2 flex justify-end">
                  <button
                    type="button"
                    className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                    onClick={generatePreview}
                  >
                    Refresh
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-4">
                <p className="text-gray-500 mb-2">No preview available</p>
                <button
                  type="button"
                  className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
                  onClick={generatePreview}
                >
                  Generate Preview
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Validation section */}
      <div className="mb-4">
        <div
          className="flex justify-between items-center cursor-pointer py-2 border-b"
          onClick={() => toggleSection('validation')}
        >
          <h4 className="font-medium text-gray-700">Validation</h4>
          <div className="flex items-center">
            <span className={`w-2 h-2 rounded-full ${validationResults.valid ? 'bg-green-500' : 'bg-red-500'} mr-2`}></span>
            <i className={`fas fa-chevron-${expandedSections.validation ? 'down' : 'right'} text-gray-500`}></i>
          </div>
        </div>

        {expandedSections.validation && (
          <div className="py-2">
            {validationResults.valid ? (
              <div className="p-3 bg-green-50 text-green-700 rounded border border-green-200 text-sm">
                <i className="fas fa-check-circle mr-1"></i> All configuration values are valid
              </div>
            ) : (
              <div className="p-3 bg-red-50 text-red-600 rounded border border-red-200 text-sm">
                <div className="font-medium mb-1">Please fix the following errors:</div>
                <ul className="list-disc pl-5">
                  {validationResults.errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
      </form>
    </div>
  );
};

export default PropertiesPanel;
