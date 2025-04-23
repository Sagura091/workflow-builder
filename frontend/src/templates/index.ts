/**
 * Workflow Templates
 *
 * This file contains template definitions for the workflow builder.
 */

import { Workflow } from '../types/types';

// Template categories
export enum TemplateCategory {
  DATA_PROCESSING = 'Data Processing',
  MACHINE_LEARNING = 'Machine Learning',
  WEB_AUTOMATION = 'Web Automation',
  API_INTEGRATION = 'API Integration',
  TEXT_PROCESSING = 'Text Processing',
  UTILITIES = 'Utilities'
}

// Template difficulty levels
export enum TemplateDifficulty {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced'
}

// Template interface
export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: TemplateCategory;
  difficulty: TemplateDifficulty;
  tags: string[];
  thumbnail?: string;
  workflow: Workflow;
  created_by: string;
  created_at: string;
  updated_at?: string;
  usage_count: number;
}

// Sample templates
export const templates: WorkflowTemplate[] = [
  {
    id: 'template-1',
    name: 'Simple Data Processing',
    description: 'A basic workflow for loading, transforming, and saving data',
    category: TemplateCategory.DATA_PROCESSING,
    difficulty: TemplateDifficulty.BEGINNER,
    tags: ['csv', 'data', 'beginner'],
    workflow: {
      id: null,
      name: 'Simple Data Processing',
      nodes: [
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
          type: 'core.data.csv_loader',
          x: 400,
          y: 200,
          config: {
            title: 'Load CSV',
            file_path: 'data/sample.csv'
          }
        },
        {
          id: 'node-3',
          type: 'core.data.filter',
          x: 700,
          y: 200,
          config: {
            title: 'Filter Data',
            condition: 'value > 10'
          }
        },
        {
          id: 'node-4',
          type: 'core.data.csv_writer',
          x: 1000,
          y: 200,
          config: {
            title: 'Save CSV',
            file_path: 'data/filtered.csv'
          }
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
          from: { nodeId: 'node-3', port: 'filtered' },
          to: { nodeId: 'node-4', port: 'data' }
        }
      ]
    },
    created_by: 'system',
    created_at: '2023-01-01T00:00:00Z',
    usage_count: 120
  },
  {
    id: 'template-2',
    name: 'Basic ML Pipeline',
    description: 'A simple machine learning workflow for training and evaluating a model',
    category: TemplateCategory.MACHINE_LEARNING,
    difficulty: TemplateDifficulty.INTERMEDIATE,
    tags: ['ml', 'training', 'evaluation'],
    workflow: {
      id: null,
      name: 'Basic ML Pipeline',
      nodes: [
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
          type: 'core.data.dataset_loader',
          x: 400,
          y: 200,
          config: {
            title: 'Load Dataset',
            dataset: 'iris'
          }
        },
        {
          id: 'node-3',
          type: 'core.ml.split_data',
          x: 700,
          y: 200,
          config: {
            title: 'Split Data',
            test_size: 0.2,
            random_state: 42
          }
        },
        {
          id: 'node-4',
          type: 'core.ml.train_model',
          x: 1000,
          y: 100,
          config: {
            title: 'Train Model',
            model_type: 'Random Forest',
            hyperparams: '{"n_estimators": 100, "max_depth": 5}'
          }
        },
        {
          id: 'node-5',
          type: 'core.ml.evaluate',
          x: 1300,
          y: 200,
          config: {
            title: 'Evaluate Model',
            metrics: ['Accuracy', 'Precision', 'Recall']
          }
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
          from: { nodeId: 'node-3', port: 'train_data' },
          to: { nodeId: 'node-4', port: 'data' }
        },
        {
          id: 'conn-4',
          from: { nodeId: 'node-4', port: 'model' },
          to: { nodeId: 'node-5', port: 'model' }
        },
        {
          id: 'conn-5',
          from: { nodeId: 'node-3', port: 'test_data' },
          to: { nodeId: 'node-5', port: 'test_data' }
        }
      ]
    },
    created_by: 'system',
    created_at: '2023-01-15T00:00:00Z',
    usage_count: 85
  },
  {
    id: 'template-3',
    name: 'API Data Fetcher',
    description: 'Fetch data from an API and process the results',
    category: TemplateCategory.API_INTEGRATION,
    difficulty: TemplateDifficulty.BEGINNER,
    tags: ['api', 'http', 'json'],
    workflow: {
      id: null,
      name: 'API Data Fetcher',
      nodes: [
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
          type: 'core.web.http_request',
          x: 400,
          y: 200,
          config: {
            title: 'Fetch API Data',
            url: 'https://api.example.com/data',
            method: 'GET',
            headers: '{"Authorization": "Bearer ${token}"}'
          }
        },
        {
          id: 'node-3',
          type: 'core.data.json_parser',
          x: 700,
          y: 200,
          config: {
            title: 'Parse JSON',
            path: 'data.items'
          }
        },
        {
          id: 'node-4',
          type: 'core.data.data_mapper',
          x: 1000,
          y: 200,
          config: {
            title: 'Map Data',
            mapping: '{"id": "$.id", "name": "$.title", "value": "$.amount"}'
          }
        },
        {
          id: 'node-5',
          type: 'core.data.csv_writer',
          x: 1300,
          y: 200,
          config: {
            title: 'Save as CSV',
            file_path: 'data/api_results.csv'
          }
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
          from: { nodeId: 'node-2', port: 'response' },
          to: { nodeId: 'node-3', port: 'json' }
        },
        {
          id: 'conn-3',
          from: { nodeId: 'node-3', port: 'data' },
          to: { nodeId: 'node-4', port: 'input' }
        },
        {
          id: 'conn-4',
          from: { nodeId: 'node-4', port: 'output' },
          to: { nodeId: 'node-5', port: 'data' }
        }
      ]
    },
    created_by: 'system',
    created_at: '2023-02-10T00:00:00Z',
    usage_count: 65
  }
];