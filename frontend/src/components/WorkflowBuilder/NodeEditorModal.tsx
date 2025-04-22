import React, { useState, useEffect } from 'react';
import { NodeData, Plugin, ConfigField } from '../../types';
import { useNodeTypes } from '../../contexts/NodeTypesContext';
import { useNodeConfig } from '../../contexts/NodeConfigContext';
import CodeEditor from '../FormControls/CodeEditor';

interface NodeEditorModalProps {
  nodeId: string;
  node: NodeData | undefined;
  plugins: Plugin[];
  onSave: (config: Record<string, any>) => void;
  onCancel: () => void;
}

const NodeEditorModal: React.FC<NodeEditorModalProps> = ({
  nodeId,
  node,
  plugins,
  onSave,
  onCancel
}) => {
  const [config, setConfig] = useState<Record<string, any>>({});
  const { getConfigForNode } = useNodeConfig();

  // Initialize form with node config
  useEffect(() => {
    if (node) {
      setConfig(node.config || {});
    }
  }, [node]);

  if (!node) return null;

  // Get node type information
  const getNodeTypeInfo = (type: string) => {
    // First try to get config from NodeConfigContext
    const nodeConfig = getConfigForNode(type);
    if (nodeConfig && nodeConfig.config_fields) {
      return {
        title: type.split('.').pop() || type,
        configFields: nodeConfig.config_fields.map((field: any) => ({
          name: field.id,
          label: field.name,
          type: mapFieldType(field.type),
          placeholder: field.description,
          options: field.options ? field.options.map((opt: any) => opt.label || opt.value) : undefined,
          multiple: field.type === 'multi_select',
          min: field.validation?.min,
          step: field.validation?.step,
          required: field.required
        }))
      };
    }

    // Check if it's a plugin
    const plugin = plugins.find(p => p.id === type);
    if (plugin && plugin.__plugin_meta__) {
      return {
        title: plugin.__plugin_meta__.name,
        configFields: plugin.__plugin_meta__.configFields
      };
    }

    // Default
    return { title: type.split('.').pop() || type, configFields: [] };
  };

  // Map backend field types to frontend field types
  const mapFieldType = (backendType: string): string => {
    const typeMap: Record<string, string> = {
      'string': 'text',
      'number': 'number',
      'boolean': 'checkbox',
      'select': 'select',
      'multi_select': 'select',
      'code': 'code',
      'color': 'color',
      'textarea': 'textarea',
      'json': 'code'
    };

    return typeMap[backendType] || 'text';
  };

  const { title, configFields } = getNodeTypeInfo(node.type);

  // Handle form field change
  const handleFieldChange = (name: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      [name]: value
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
            className="w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
            className="w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
            className="w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
            className="w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
            className="w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
        );

      case 'checkbox':
        return (
          <div className="flex items-center">
            <input
              type="checkbox"
              name={field.name}
              id={field.name}
              checked={!!value}
              onChange={(e) => handleFieldChange(field.name, e.target.checked)}
              className="h-4 w-4 text-blue-600 rounded"
            />
            <label htmlFor={field.name} className="ml-2 text-sm text-gray-700">{field.label}</label>
          </div>
        );

      case 'code':
        return (
          <CodeEditor
            value={value as string}
            onChange={(newValue) => handleFieldChange(field.name, newValue)}
            language="json"
            height="150px"
            placeholder={field.placeholder || ''}
          />
        );

      case 'color':
        return (
          <input
            type="color"
            name={field.name}
            value={value as string}
            onChange={(e) => handleFieldChange(field.name, e.target.value)}
            className="w-full h-10 border rounded-md px-1 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        );

      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Edit {title}</h3>
          <button
            className="text-gray-500 hover:text-gray-700"
            onClick={onCancel}
          >
            <i className="fas fa-times"></i>
          </button>
        </div>

        <div className="space-y-4">
          {configFields.map((field: ConfigField) => (
            <div key={field.name} className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">{field.label}</label>
              {renderField(field)}
            </div>
          ))}
        </div>

        <div className="mt-6 flex justify-end space-x-2">
          <button
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
            onClick={onCancel}
          >
            Cancel
          </button>
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            onClick={() => onSave(config)}
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};

export default NodeEditorModal;
