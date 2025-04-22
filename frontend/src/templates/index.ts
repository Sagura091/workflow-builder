import { Workflow } from '../types';

// Template categories
export enum TemplateCategory {
  BASIC = 'Basic',
  DATA_PROCESSING = 'Data Processing',
  MACHINE_LEARNING = 'Machine Learning',
  WEB_INTEGRATION = 'Web Integration',
  AUTOMATION = 'Automation',
}

// Template interface
export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: TemplateCategory;
  tags: string[];
  workflow: Workflow;
  thumbnail?: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  createdBy?: string;
}

// Basic "Hello World" template
const helloWorldTemplate: WorkflowTemplate = {
  id: 'hello-world',
  name: 'Hello World',
  description: 'A simple workflow that outputs "Hello World"',
  category: TemplateCategory.BASIC,
  tags: ['beginner', 'text'],
  difficulty: 'beginner',
  workflow: {
    id: null,
    name: 'Hello World',
    description: 'A simple workflow that outputs "Hello World"',
    nodes: [
      {
        id: 'node-1',
        type: 'core.begin',
        x: 100,
        y: 200,
        config: {}
      },
      {
        id: 'node-2',
        type: 'core.text.constant',
        x: 400,
        y: 200,
        config: {
          value: 'Hello World'
        }
      },
      {
        id: 'node-3',
        type: 'core.end',
        x: 700,
        y: 200,
        config: {}
      }
    ],
    connections: [
      {
        id: 'conn-1',
        from: { nodeId: 'node-1', port: 'trigger' },
        to: { nodeId: 'node-2', port: 'trigger' }
      },
      {
        id: 'conn-2',
        from: { nodeId: 'node-2', port: 'output' },
        to: { nodeId: 'node-3', port: 'result' }
      },
      {
        id: 'conn-3',
        from: { nodeId: 'node-2', port: 'trigger' },
        to: { nodeId: 'node-3', port: 'trigger' }
      }
    ]
  }
};

// Data processing template
const dataProcessingTemplate: WorkflowTemplate = {
  id: 'data-processing',
  name: 'CSV Data Processing',
  description: 'Load a CSV file, filter rows, and calculate statistics',
  category: TemplateCategory.DATA_PROCESSING,
  tags: ['csv', 'filter', 'statistics'],
  difficulty: 'intermediate',
  workflow: {
    id: null,
    name: 'CSV Data Processing',
    description: 'Load a CSV file, filter rows, and calculate statistics',
    nodes: [
      {
        id: 'node-1',
        type: 'core.begin',
        x: 100,
        y: 200,
        config: {}
      },
      {
        id: 'node-2',
        type: 'core.file_storage.load_csv',
        x: 350,
        y: 200,
        config: {
          filepath: 'data/sample.csv'
        }
      },
      {
        id: 'node-3',
        type: 'core.data.filter',
        x: 600,
        y: 200,
        config: {
          column: 'age',
          operator: '>',
          value: 30
        }
      },
      {
        id: 'node-4',
        type: 'core.data.statistics',
        x: 850,
        y: 200,
        config: {
          columns: ['income', 'age'],
          operations: ['mean', 'median', 'std']
        }
      },
      {
        id: 'node-5',
        type: 'core.end',
        x: 1100,
        y: 200,
        config: {}
      }
    ],
    connections: [
      {
        id: 'conn-1',
        from: { nodeId: 'node-1', port: 'trigger' },
        to: { nodeId: 'node-2', port: 'trigger' }
      },
      {
        id: 'conn-2',
        from: { nodeId: 'node-2', port: 'data' },
        to: { nodeId: 'node-3', port: 'data' }
      },
      {
        id: 'conn-3',
        from: { nodeId: 'node-2', port: 'trigger' },
        to: { nodeId: 'node-3', port: 'trigger' }
      },
      {
        id: 'conn-4',
        from: { nodeId: 'node-3', port: 'filtered_data' },
        to: { nodeId: 'node-4', port: 'data' }
      },
      {
        id: 'conn-5',
        from: { nodeId: 'node-3', port: 'trigger' },
        to: { nodeId: 'node-4', port: 'trigger' }
      },
      {
        id: 'conn-6',
        from: { nodeId: 'node-4', port: 'statistics' },
        to: { nodeId: 'node-5', port: 'result' }
      },
      {
        id: 'conn-7',
        from: { nodeId: 'node-4', port: 'trigger' },
        to: { nodeId: 'node-5', port: 'trigger' }
      }
    ]
  }
};

// Web API integration template
const webApiTemplate: WorkflowTemplate = {
  id: 'web-api',
  name: 'Weather API Integration',
  description: 'Fetch weather data from an API and process the results',
  category: TemplateCategory.WEB_INTEGRATION,
  tags: ['api', 'weather', 'json'],
  difficulty: 'intermediate',
  workflow: {
    id: null,
    name: 'Weather API Integration',
    description: 'Fetch weather data from an API and process the results',
    nodes: [
      {
        id: 'node-1',
        type: 'core.begin',
        x: 100,
        y: 200,
        config: {}
      },
      {
        id: 'node-2',
        type: 'core.text.constant',
        x: 350,
        y: 100,
        config: {
          value: 'London'
        }
      },
      {
        id: 'node-3',
        type: 'core.web_api.http_request',
        x: 600,
        y: 200,
        config: {
          method: 'GET',
          url: 'https://api.openweathermap.org/data/2.5/weather',
          params: {
            q: '{city}',
            appid: 'YOUR_API_KEY',
            units: 'metric'
          }
        }
      },
      {
        id: 'node-4',
        type: 'core.data.extract',
        x: 850,
        y: 200,
        config: {
          path: 'main.temp'
        }
      },
      {
        id: 'node-5',
        type: 'core.text.template',
        x: 1100,
        y: 200,
        config: {
          template: 'The temperature in {city} is {temp}°C'
        }
      },
      {
        id: 'node-6',
        type: 'core.end',
        x: 1350,
        y: 200,
        config: {}
      }
    ],
    connections: [
      {
        id: 'conn-1',
        from: { nodeId: 'node-1', port: 'trigger' },
        to: { nodeId: 'node-2', port: 'trigger' }
      },
      {
        id: 'conn-2',
        from: { nodeId: 'node-2', port: 'output' },
        to: { nodeId: 'node-3', port: 'city' }
      },
      {
        id: 'conn-3',
        from: { nodeId: 'node-2', port: 'trigger' },
        to: { nodeId: 'node-3', port: 'trigger' }
      },
      {
        id: 'conn-4',
        from: { nodeId: 'node-3', port: 'response' },
        to: { nodeId: 'node-4', port: 'data' }
      },
      {
        id: 'conn-5',
        from: { nodeId: 'node-3', port: 'trigger' },
        to: { nodeId: 'node-4', port: 'trigger' }
      },
      {
        id: 'conn-6',
        from: { nodeId: 'node-4', port: 'value' },
        to: { nodeId: 'node-5', port: 'temp' }
      },
      {
        id: 'conn-7',
        from: { nodeId: 'node-2', port: 'output' },
        to: { nodeId: 'node-5', port: 'city' }
      },
      {
        id: 'conn-8',
        from: { nodeId: 'node-4', port: 'trigger' },
        to: { nodeId: 'node-5', port: 'trigger' }
      },
      {
        id: 'conn-9',
        from: { nodeId: 'node-5', port: 'output' },
        to: { nodeId: 'node-6', port: 'result' }
      },
      {
        id: 'conn-10',
        from: { nodeId: 'node-5', port: 'trigger' },
        to: { nodeId: 'node-6', port: 'trigger' }
      }
    ]
  }
};

// Machine learning template
const mlTemplate: WorkflowTemplate = {
  id: 'ml-classification',
  name: 'Simple Classification Model',
  description: 'Train a classification model on the Iris dataset',
  category: TemplateCategory.MACHINE_LEARNING,
  tags: ['machine learning', 'classification', 'iris'],
  difficulty: 'advanced',
  workflow: {
    id: null,
    name: 'Simple Classification Model',
    description: 'Train a classification model on the Iris dataset',
    nodes: [
      {
        id: 'node-1',
        type: 'core.begin',
        x: 100,
        y: 200,
        config: {}
      },
      {
        id: 'node-2',
        type: 'core.data.load_dataset',
        x: 350,
        y: 200,
        config: {
          dataset: 'iris'
        }
      },
      {
        id: 'node-3',
        type: 'core.data.split',
        x: 600,
        y: 200,
        config: {
          test_size: 0.2,
          random_state: 42
        }
      },
      {
        id: 'node-4',
        type: 'core.ml.train_model',
        x: 850,
        y: 200,
        config: {
          model_type: 'RandomForest',
          hyperparams: {
            n_estimators: 100,
            max_depth: 5
          }
        }
      },
      {
        id: 'node-5',
        type: 'core.ml.evaluate',
        x: 1100,
        y: 200,
        config: {
          metrics: ['accuracy', 'precision', 'recall', 'f1']
        }
      },
      {
        id: 'node-6',
        type: 'core.end',
        x: 1350,
        y: 200,
        config: {}
      }
    ],
    connections: [
      {
        id: 'conn-1',
        from: { nodeId: 'node-1', port: 'trigger' },
        to: { nodeId: 'node-2', port: 'trigger' }
      },
      {
        id: 'conn-2',
        from: { nodeId: 'node-2', port: 'dataset' },
        to: { nodeId: 'node-3', port: 'dataset' }
      },
      {
        id: 'conn-3',
        from: { nodeId: 'node-2', port: 'trigger' },
        to: { nodeId: 'node-3', port: 'trigger' }
      },
      {
        id: 'conn-4',
        from: { nodeId: 'node-3', port: 'train_data' },
        to: { nodeId: 'node-4', port: 'train_data' }
      },
      {
        id: 'conn-5',
        from: { nodeId: 'node-3', port: 'test_data' },
        to: { nodeId: 'node-5', port: 'test_data' }
      },
      {
        id: 'conn-6',
        from: { nodeId: 'node-3', port: 'trigger' },
        to: { nodeId: 'node-4', port: 'trigger' }
      },
      {
        id: 'conn-7',
        from: { nodeId: 'node-4', port: 'model' },
        to: { nodeId: 'node-5', port: 'model' }
      },
      {
        id: 'conn-8',
        from: { nodeId: 'node-4', port: 'trigger' },
        to: { nodeId: 'node-5', port: 'trigger' }
      },
      {
        id: 'conn-9',
        from: { nodeId: 'node-5', port: 'metrics' },
        to: { nodeId: 'node-6', port: 'result' }
      },
      {
        id: 'conn-10',
        from: { nodeId: 'node-5', port: 'trigger' },
        to: { nodeId: 'node-6', port: 'trigger' }
      }
    ]
  }
};

// Automation template
const automationTemplate: WorkflowTemplate = {
  id: 'file-automation',
  name: 'File Processing Automation',
  description: 'Watch a directory for new files, process them, and save the results',
  category: TemplateCategory.AUTOMATION,
  tags: ['file', 'automation', 'processing'],
  difficulty: 'intermediate',
  workflow: {
    id: null,
    name: 'File Processing Automation',
    description: 'Watch a directory for new files, process them, and save the results',
    nodes: [
      {
        id: 'node-1',
        type: 'core.begin',
        x: 100,
        y: 200,
        config: {}
      },
      {
        id: 'node-2',
        type: 'core.file_storage.watch_directory',
        x: 350,
        y: 200,
        config: {
          directory: './input',
          pattern: '*.csv'
        }
      },
      {
        id: 'node-3',
        type: 'core.file_storage.load_csv',
        x: 600,
        y: 200,
        config: {}
      },
      {
        id: 'node-4',
        type: 'core.data.transform',
        x: 850,
        y: 200,
        config: {
          transformations: [
            { column: 'price', operation: 'multiply', value: 1.1 },
            { column: 'date', operation: 'format', format: 'YYYY-MM-DD' }
          ]
        }
      },
      {
        id: 'node-5',
        type: 'core.file_storage.save_csv',
        x: 1100,
        y: 200,
        config: {
          directory: './output'
        }
      },
      {
        id: 'node-6',
        type: 'core.end',
        x: 1350,
        y: 200,
        config: {}
      }
    ],
    connections: [
      {
        id: 'conn-1',
        from: { nodeId: 'node-1', port: 'trigger' },
        to: { nodeId: 'node-2', port: 'trigger' }
      },
      {
        id: 'conn-2',
        from: { nodeId: 'node-2', port: 'file_path' },
        to: { nodeId: 'node-3', port: 'filepath' }
      },
      {
        id: 'conn-3',
        from: { nodeId: 'node-2', port: 'trigger' },
        to: { nodeId: 'node-3', port: 'trigger' }
      },
      {
        id: 'conn-4',
        from: { nodeId: 'node-3', port: 'data' },
        to: { nodeId: 'node-4', port: 'data' }
      },
      {
        id: 'conn-5',
        from: { nodeId: 'node-3', port: 'trigger' },
        to: { nodeId: 'node-4', port: 'trigger' }
      },
      {
        id: 'conn-6',
        from: { nodeId: 'node-4', port: 'transformed_data' },
        to: { nodeId: 'node-5', port: 'data' }
      },
      {
        id: 'conn-7',
        from: { nodeId: 'node-2', port: 'filename' },
        to: { nodeId: 'node-5', port: 'filename' }
      },
      {
        id: 'conn-8',
        from: { nodeId: 'node-4', port: 'trigger' },
        to: { nodeId: 'node-5', port: 'trigger' }
      },
      {
        id: 'conn-9',
        from: { nodeId: 'node-5', port: 'filepath' },
        to: { nodeId: 'node-6', port: 'result' }
      },
      {
        id: 'conn-10',
        from: { nodeId: 'node-5', port: 'trigger' },
        to: { nodeId: 'node-6', port: 'trigger' }
      }
    ]
  }
};

// Export all templates
export const templates: WorkflowTemplate[] = [
  helloWorldTemplate,
  dataProcessingTemplate,
  webApiTemplate,
  mlTemplate,
  automationTemplate
];

// Get all templates
export const getAllTemplates = (): WorkflowTemplate[] => {
  return templates;
};

// Get template by ID
export const getTemplateById = (id: string): WorkflowTemplate | undefined => {
  return templates.find(template => template.id === id);
};

// Get templates by category
export const getTemplatesByCategory = (category: TemplateCategory): WorkflowTemplate[] => {
  return templates.filter(template => template.category === category);
};

// Get templates by tag
export const getTemplatesByTag = (tag: string): WorkflowTemplate[] => {
  return templates.filter(template => template.tags.includes(tag));
};

// Get templates by difficulty
export const getTemplatesByDifficulty = (difficulty: 'beginner' | 'intermediate' | 'advanced'): WorkflowTemplate[] => {
  return templates.filter(template => template.difficulty === difficulty);
};
