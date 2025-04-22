// Mock data for fallback when API is not available
import { DiscoveredNode } from '../services/nodeDiscovery';
import { NodeTypeDefinition } from '../types';

// Core nodes for fallback
export const coreNodes: any[] = [
    {
      id: 'core.begin',
      name: 'Begin',
      category: 'CONTROL_FLOW',
      description: 'Starting point of the workflow',
      status: 'available',
      isCore: true,
      inputs: [],
      outputs: [
        { id: 'trigger', name: 'Trigger', type: 'trigger' },
        { id: 'workflow_id', name: 'Workflow ID', type: 'string' },
        { id: 'timestamp', name: 'Timestamp', type: 'number' }
      ],
      ui_properties: {
        color: '#2ecc71',
        icon: 'play',
        width: 240
      }
    },
    {
      id: 'core.end',
      name: 'End',
      category: 'CONTROL_FLOW',
      description: 'Ending point of the workflow',
      status: 'available',
      isCore: true,
      inputs: [
        { id: 'trigger', name: 'Trigger', type: 'trigger', required: true },
        { id: 'result', name: 'Result', type: 'any' }
      ],
      outputs: [
        { id: 'workflow_id', name: 'Workflow ID', type: 'string' },
        { id: 'execution_time', name: 'Execution Time', type: 'number' }
      ],
      ui_properties: {
        color: '#e74c3c',
        icon: 'stop',
        width: 240
      }
    },
    {
      id: 'core.conditional',
      name: 'Conditional',
      category: 'CONTROL_FLOW',
      description: 'Branch based on a condition',
      status: 'available',
      isCore: true,
      inputs: [
        { id: 'trigger', name: 'Trigger', type: 'trigger' },
        { id: 'condition', name: 'Condition', type: 'boolean', required: true }
      ],
      outputs: [
        { id: 'true', name: 'True', type: 'trigger' },
        { id: 'false', name: 'False', type: 'trigger' }
      ],
      ui_properties: {
        color: '#f39c12',
        icon: 'code-branch',
        width: 240
      }
    },
    {
      id: 'core.text_input',
      name: 'Text Input',
      category: 'TEXT',
      description: 'Enter text manually',
      status: 'available',
      isCore: true,
      inputs: [
        { id: 'trigger', name: 'Trigger', type: 'trigger' }
      ],
      outputs: [
        { id: 'text', name: 'Text', type: 'string' },
        { id: 'length', name: 'Length', type: 'number' }
      ],
      ui_properties: {
        color: '#3498db',
        icon: 'font',
        width: 240
      }
    },
    {
      id: 'core.text_output',
      name: 'Text Output',
      category: 'TEXT',
      description: 'Display text results',
      status: 'available',
      isCore: true,
      inputs: [
        { id: 'text', name: 'Text', type: 'string', required: true },
        { id: 'trigger', name: 'Trigger', type: 'trigger' }
      ],
      outputs: [
        { id: 'text', name: 'Text', type: 'string' }
      ],
      ui_properties: {
        color: '#e74c3c',
        icon: 'comment',
        width: 240
      }
    }
  ];

// Plugins for fallback
export const plugins: any[] = [
    {
      id: 'plugin.text_transform',
      name: 'Text Transform',
      category: 'TEXT',
      description: 'Transform text (uppercase, lowercase, etc.)',
      status: 'available',
      isCore: false,
      inputs: [
        { id: 'text', name: 'Text', type: 'string', required: true },
        { id: 'transform_type', name: 'Transform Type', type: 'string', required: true },
        { id: 'trigger', name: 'Trigger', type: 'trigger' }
      ],
      outputs: [
        { id: 'transformed_text', name: 'Transformed Text', type: 'string' }
      ],
      ui_properties: {
        color: '#9b59b6',
        icon: 'text-height',
        width: 240
      }
    },
    {
      id: 'plugin.math_operation',
      name: 'Math Operation',
      category: 'MATH',
      description: 'Perform math operations',
      status: 'available',
      isCore: false,
      inputs: [
        { id: 'a', name: 'A', type: 'number', required: true },
        { id: 'b', name: 'B', type: 'number', required: true },
        { id: 'operation', name: 'Operation', type: 'string', required: true },
        { id: 'trigger', name: 'Trigger', type: 'trigger' }
      ],
      outputs: [
        { id: 'result', name: 'Result', type: 'number' }
      ],
      ui_properties: {
        color: '#f1c40f',
        icon: 'calculator',
        width: 240
      }
    },
    {
      id: 'plugin.data_filter',
      name: 'Data Filter',
      category: 'DATA',
      description: 'Filter data based on conditions',
      status: 'available',
      isCore: false,
      inputs: [
        { id: 'data', name: 'Data', type: 'array', required: true },
        { id: 'filter_condition', name: 'Filter Condition', type: 'string', required: true },
        { id: 'trigger', name: 'Trigger', type: 'trigger' }
      ],
      outputs: [
        { id: 'filtered_data', name: 'Filtered Data', type: 'array' }
      ],
      ui_properties: {
        color: '#1abc9c',
        icon: 'filter',
        width: 240
      }
    }
  ];

// Type system for fallback
export const typeSystem = {
  types: {
    string: { name: 'String', description: 'Text value' },
    number: { name: 'Number', description: 'Numeric value' },
    boolean: { name: 'Boolean', description: 'True/false value' },
    object: { name: 'Object', description: 'JavaScript object' },
    array: { name: 'Array', description: 'List of values' },
    any: { name: 'Any', description: 'Any type of value' },
    trigger: { name: 'Trigger', description: 'Execution trigger' }
  },
  rules: [
    { source: 'string', target: ['string', 'any'], bidirectional: false },
    { source: 'number', target: ['number', 'string', 'any'], bidirectional: false },
    { source: 'boolean', target: ['boolean', 'string', 'any'], bidirectional: false },
    { source: 'object', target: ['object', 'any'], bidirectional: false },
    { source: 'array', target: ['array', 'any'], bidirectional: false },
    { source: 'trigger', target: ['trigger'], bidirectional: true },
    { source: 'any', target: ['string', 'number', 'boolean', 'object', 'array', 'any'], bidirectional: true }
  ]
};

// Combined mock data for convenience
export const mockNodeTypes = {
  coreNodes,
  plugins
};
