import { NodeData, Connection, Plugin, ConfigField } from '../types';
import { v4 as uuidv4 } from 'uuid';

// Mock node types for the demo
export const mockNodeTypes = [
  {
    type: 'core.begin',
    name: 'Begin',
    category: 'Flow',
    description: 'Starting point of the workflow',
    icon: 'play-circle',
    color: 'blue',
    inputs: [],
    outputs: [
      { name: 'output', type: 'trigger', description: 'Execution output' }
    ],
    configFields: []
  },
  {
    type: 'core.text.text_input',
    name: 'Text Input',
    category: 'Text',
    description: 'Provides a text value',
    icon: 'font',
    color: 'blue',
    inputs: [],
    outputs: [
      { name: 'text', type: 'string', description: 'The text value' }
    ],
    configFields: [
      { name: 'text', label: 'Text', type: 'textarea', placeholder: 'Enter text...' }
    ]
  },
  {
    type: 'core.text.text_template',
    name: 'Text Template',
    category: 'Text',
    description: 'Creates text using a template with variables',
    icon: 'file-alt',
    color: 'blue',
    inputs: [
      { name: 'variables', type: 'object', description: 'Variables to use in the template' }
    ],
    outputs: [
      { name: 'text', type: 'string', description: 'The resulting text' }
    ],
    configFields: [
      { name: 'template', label: 'Template', type: 'textarea', placeholder: 'Enter template with {{variables}}...' }
    ]
  },
  {
    type: 'core.variables.set_variable',
    name: 'Set Variable',
    category: 'Variables',
    description: 'Sets a variable value',
    icon: 'database',
    color: 'purple',
    inputs: [
      { name: 'value', type: 'any', description: 'The value to store' }
    ],
    outputs: [
      { name: 'output', type: 'any', description: 'The stored value' }
    ],
    configFields: [
      { name: 'name', label: 'Variable Name', type: 'text', placeholder: 'Enter variable name...' }
    ]
  },
  {
    type: 'core.variables.get_variable',
    name: 'Get Variable',
    category: 'Variables',
    description: 'Gets a variable value',
    icon: 'database',
    color: 'purple',
    inputs: [],
    outputs: [
      { name: 'value', type: 'any', description: 'The variable value' }
    ],
    configFields: [
      { name: 'name', label: 'Variable Name', type: 'text', placeholder: 'Enter variable name...' }
    ]
  },
  {
    type: 'core.control_flow.if_condition',
    name: 'If Condition',
    category: 'Control Flow',
    description: 'Branches based on a condition',
    icon: 'code-branch',
    color: 'orange',
    inputs: [
      { name: 'condition', type: 'boolean', description: 'The condition to evaluate' }
    ],
    outputs: [
      { name: 'true', type: 'trigger', description: 'Executed if condition is true' },
      { name: 'false', type: 'trigger', description: 'Executed if condition is false' }
    ],
    configFields: []
  },
  {
    type: 'core.control_flow.for_loop',
    name: 'For Loop',
    category: 'Control Flow',
    description: 'Loops over a list of items',
    icon: 'redo',
    color: 'orange',
    inputs: [
      { name: 'items', type: 'array', description: 'The items to loop over' }
    ],
    outputs: [
      { name: 'item', type: 'any', description: 'The current item' },
      { name: 'index', type: 'number', description: 'The current index' },
      { name: 'completed', type: 'trigger', description: 'Executed when loop completes' }
    ],
    configFields: []
  },
  {
    type: 'core.math.calculator',
    name: 'Calculator',
    category: 'Math',
    description: 'Performs math operations',
    icon: 'calculator',
    color: 'green',
    inputs: [
      { name: 'a', type: 'number', description: 'First value' },
      { name: 'b', type: 'number', description: 'Second value' }
    ],
    outputs: [
      { name: 'result', type: 'number', description: 'The result' }
    ],
    configFields: [
      {
        name: 'operation',
        label: 'Operation',
        type: 'select',
        options: ['add', 'subtract', 'multiply', 'divide']
      }
    ]
  },
  {
    type: 'core.web_api.http_request',
    name: 'HTTP Request',
    category: 'Web & API',
    description: 'Makes an HTTP request',
    icon: 'globe',
    color: 'pink',
    inputs: [
      { name: 'url', type: 'string', description: 'The URL to request' },
      { name: 'headers', type: 'object', description: 'Request headers' },
      { name: 'body', type: 'any', description: 'Request body' }
    ],
    outputs: [
      { name: 'response', type: 'object', description: 'The response data' },
      { name: 'status', type: 'number', description: 'The HTTP status code' }
    ],
    configFields: [
      {
        name: 'method',
        label: 'Method',
        type: 'select',
        options: ['GET', 'POST', 'PUT', 'DELETE']
      },
      { name: 'url', label: 'URL', type: 'text', placeholder: 'https://...' }
    ]
  },
  {
    type: 'core.file_storage.read_file',
    name: 'Read File',
    category: 'File Storage',
    description: 'Reads a file from storage',
    icon: 'file',
    color: 'yellow',
    inputs: [
      { name: 'path', type: 'string', description: 'File path' }
    ],
    outputs: [
      { name: 'content', type: 'string', description: 'File content' }
    ],
    configFields: [
      { name: 'path', label: 'File Path', type: 'text', placeholder: '/path/to/file.txt' }
    ]
  },
  {
    type: 'plugins.ai.text_generation',
    name: 'AI Text Generation',
    category: 'AI & ML',
    description: 'Generates text using AI',
    icon: 'robot',
    color: 'indigo',
    inputs: [
      { name: 'prompt', type: 'string', description: 'The prompt for generation' }
    ],
    outputs: [
      { name: 'text', type: 'string', description: 'Generated text' }
    ],
    configFields: [
      { name: 'model', label: 'Model', type: 'select', options: ['gpt-3.5-turbo', 'gpt-4'] },
      { name: 'temperature', label: 'Temperature', type: 'number', min: 0, step: 0.1 }
    ]
  },
  {
    type: 'plugins.utilities.delay',
    name: 'Delay',
    category: 'Utilities',
    description: 'Adds a delay in workflow execution',
    icon: 'clock',
    color: 'gray',
    inputs: [
      { name: 'input', type: 'any', description: 'Input to pass through after delay' }
    ],
    outputs: [
      { name: 'output', type: 'any', description: 'The delayed input' }
    ],
    configFields: [
      { name: 'seconds', label: 'Seconds', type: 'number', min: 0, step: 0.1 }
    ]
  }
];

// Create a sample workflow with a few connected nodes
export const createSampleWorkflow = (): { nodes: NodeData[], connections: Connection[] } => {
  // Create nodes with title in the config to avoid TypeScript errors
  const nodes: NodeData[] = [
    {
      id: 'node-1',
      type: 'core.begin',
      x: 100,
      y: 200,
      config: {
        title: 'Begin'
      }
    },
    {
      id: 'node-2',
      type: 'core.text.text_input',
      x: 400,
      y: 100,
      config: {
        title: 'User Prompt',
        text: 'Tell me about workflow automation'
      }
    },
    {
      id: 'node-3',
      type: 'plugins.ai.text_generation',
      x: 700,
      y: 200,
      config: {
        title: 'Generate Response',
        model: 'gpt-4',
        temperature: 0.7
      }
    },
    {
      id: 'node-4',
      type: 'core.variables.set_variable',
      x: 1000,
      y: 200,
      config: {
        title: 'Store Result',
        name: 'ai_response'
      }
    },
    {
      id: 'node-5',
      type: 'core.control_flow.if_condition',
      x: 400,
      y: 350,
      config: {
        title: 'Check Length'
      }
    },
    {
      id: 'node-6',
      type: 'core.text.text_template',
      x: 700,
      y: 350,
      config: {
        title: 'Format Response',
        template: 'AI says: {{response}}'
      }
    }
  ];

  const connections: Connection[] = [
    {
      id: 'conn-1',
      from: { nodeId: 'node-1', port: 'output' },
      to: { nodeId: 'node-2', port: 'input' }
    },
    {
      id: 'conn-2',
      from: { nodeId: 'node-2', port: 'text' },
      to: { nodeId: 'node-3', port: 'prompt' }
    },
    {
      id: 'conn-3',
      from: { nodeId: 'node-3', port: 'text' },
      to: { nodeId: 'node-4', port: 'value' }
    },
    {
      id: 'conn-4',
      from: { nodeId: 'node-1', port: 'output' },
      to: { nodeId: 'node-5', port: 'input' }
    },
    {
      id: 'conn-5',
      from: { nodeId: 'node-3', port: 'text' },
      to: { nodeId: 'node-6', port: 'variables' }
    }
  ];

  return { nodes, connections };
};

// Helper function to convert our mock config fields to proper ConfigField type
const convertConfigFields = (fields: any[]): ConfigField[] => {
  return fields.map(field => ({
    name: field.name,
    label: field.label,
    type: field.type as 'text' | 'number' | 'select' | 'textarea' | 'checkbox',
    placeholder: field.placeholder,
    options: field.options,
    multiple: field.multiple,
    min: field.min,
    step: field.step
  }));
};

// Mock plugins for the demo
export const mockPlugins: Plugin[] = mockNodeTypes.map(nodeType => ({
  id: nodeType.type,
  __plugin_meta__: {
    name: nodeType.name,
    category: nodeType.category,
    description: nodeType.description,
    editable: true,
    generated: false,
    inputs: nodeType.inputs.reduce((acc, input) => {
      acc[input.name] = input.type;
      return acc;
    }, {} as Record<string, string>),
    outputs: nodeType.outputs.reduce((acc, output) => {
      acc[output.name] = output.type;
      return acc;
    }, {} as Record<string, string>),
    configFields: convertConfigFields(nodeType.configFields)
  }
}));

// Mock execution function
export const mockExecuteWorkflow = async (nodes: NodeData[], connections: Connection[]) => {
  // Simulate execution delay
  await new Promise(resolve => setTimeout(resolve, 1500));

  // Return mock execution results
  return {
    status: 'success',
    executionId: uuidv4(),
    results: {
      node_outputs: {
        'node-2': { text: 'Tell me about workflow automation' },
        'node-3': {
          text: 'Workflow automation is the process of using technology to automate repetitive tasks, processes, and workflows within an organization. It helps reduce manual effort, minimize errors, and increase efficiency. Modern workflow automation tools allow users to visually design workflows using a node-based interface, connecting different actions and logic together to create powerful automated processes without requiring extensive programming knowledge.'
        },
        'node-4': { output: 'Variable stored successfully' },
        'node-6': { text: 'AI says: Workflow automation is the process of using technology to automate repetitive tasks...' }
      },
      log: [
        { node: 'node-1', message: 'Workflow started', timestamp: new Date().toISOString() },
        { node: 'node-2', message: 'Text input processed', timestamp: new Date().toISOString() },
        { node: 'node-3', message: 'AI text generated', timestamp: new Date().toISOString() },
        { node: 'node-4', message: 'Variable stored', timestamp: new Date().toISOString() },
        { node: 'node-5', message: 'Condition evaluated', timestamp: new Date().toISOString() },
        { node: 'node-6', message: 'Text formatted', timestamp: new Date().toISOString() }
      ]
    }
  };
};

// Function to get node ports based on node type
export const getNodePorts = (nodeType: string) => {
  const nodeTypeInfo = mockNodeTypes.find(nt => nt.type === nodeType);

  if (!nodeTypeInfo) {
    return {
      inputs: [],
      outputs: []
    };
  }

  return {
    inputs: nodeTypeInfo.inputs,
    outputs: nodeTypeInfo.outputs
  };
};

// Function to check if two types are compatible
export const isTypeCompatible = async (fromType: string, toType: string) => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 300));

  // Simple compatibility rules for demo
  if (fromType === toType) return true;
  if (fromType === 'any' || toType === 'any') return true;
  if (fromType === 'string' && toType === 'text') return true;
  if (fromType === 'text' && toType === 'string') return true;
  if (fromType === 'number' && toType === 'integer') return true;
  if (fromType === 'integer' && toType === 'number') return true;
  if (fromType === 'object' && toType === 'json') return true;
  if (fromType === 'json' && toType === 'object') return true;

  return false;
};
