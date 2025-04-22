/**
 * Mock data for the frontend to use when the backend is not available
 */

import { NodeTypeDefinition } from '../contexts/NodeTypesContext';

/**
 * Mock node types
 */
export const mockNodeTypes = {
  coreNodes: [
    {
      id: "core.begin",
      name: "Begin",
      category: "CONTROL_FLOW",
      description: "Starting point of the workflow",
      inputs: [],
      outputs: [
        { id: "trigger", name: "Trigger", type: "trigger", ui_properties: { position: "right-top" } },
        { id: "workflow_id", name: "Workflow ID", type: "string", ui_properties: { position: "right-center" } },
        { id: "timestamp", name: "Timestamp", type: "number", ui_properties: { position: "right-bottom" } }
      ],
      ui_properties: {
        color: "#2ecc71",
        icon: "play",
        width: 240
      }
    },
    {
      id: "core.end",
      name: "End",
      category: "CONTROL_FLOW",
      description: "Ending point of the workflow",
      inputs: [
        { id: "trigger", name: "Trigger", type: "trigger", required: true, ui_properties: { position: "left-top" } },
        { id: "result", name: "Result", type: "any", ui_properties: { position: "left-center" } }
      ],
      outputs: [
        { id: "workflow_id", name: "Workflow ID", type: "string", ui_properties: { position: "right-top" } },
        { id: "execution_time", name: "Execution Time", type: "number", ui_properties: { position: "right-center" } }
      ],
      ui_properties: {
        color: "#e74c3c",
        icon: "stop",
        width: 240
      }
    },
    {
      id: "core.for_loop",
      name: "For Loop",
      category: "CONTROL_FLOW",
      description: "Iterate over a list of items",
      inputs: [
        { id: "items", name: "Items", type: "array", required: true, ui_properties: { position: "left-top" } },
        { id: "trigger", name: "Trigger", type: "trigger", required: true, ui_properties: { position: "left-center" } }
      ],
      outputs: [
        { id: "completed", name: "Completed", type: "trigger", ui_properties: { position: "right-top" } },
        { id: "current_item", name: "Current Item", type: "any", ui_properties: { position: "right-center" } },
        { id: "index", name: "Index", type: "number", ui_properties: { position: "right-bottom" } },
        { id: "results", name: "Results", type: "array", ui_properties: { position: "right-bottom" } }
      ],
      ui_properties: {
        color: "#e74c3c",
        icon: "sync",
        width: 240
      }
    },
    {
      id: "core.while_loop",
      name: "While Loop",
      category: "CONTROL_FLOW",
      description: "Execute nodes while a condition is true",
      inputs: [
        { id: "condition", name: "Condition", type: "boolean", required: true, ui_properties: { position: "left-top" } },
        { id: "trigger", name: "Trigger", type: "trigger", required: true, ui_properties: { position: "left-center" } }
      ],
      outputs: [
        { id: "completed", name: "Completed", type: "trigger", ui_properties: { position: "right-top" } },
        { id: "iteration", name: "Iteration", type: "trigger", ui_properties: { position: "right-center" } },
        { id: "iteration_count", name: "Iteration Count", type: "number", ui_properties: { position: "right-bottom" } }
      ],
      ui_properties: {
        color: "#9b59b6",
        icon: "sync-alt",
        width: 240
      }
    },
    {
      id: "core.compare",
      name: "Compare",
      category: "CONTROL_FLOW",
      description: "Compare two values and output a boolean result",
      inputs: [
        { id: "value_a", name: "Value A", type: "any", required: true, ui_properties: { position: "left-top" } },
        { id: "value_b", name: "Value B", type: "any", required: true, ui_properties: { position: "left-center" } },
        { id: "trigger", name: "Trigger", type: "trigger", ui_properties: { position: "left-bottom" } }
      ],
      outputs: [
        { id: "result", name: "Result", type: "boolean", ui_properties: { position: "right-top" } },
        { id: "true_output", name: "True", type: "trigger", ui_properties: { position: "right-center" } },
        { id: "false_output", name: "False", type: "trigger", ui_properties: { position: "right-bottom" } }
      ],
      ui_properties: {
        color: "#f39c12",
        icon: "equals",
        width: 240
      }
    },
    {
      id: "core.set_variable",
      name: "Set Variable",
      category: "VARIABLES",
      description: "Set a variable value",
      inputs: [
        { id: "value", name: "Value", type: "any", required: true, ui_properties: { position: "left-top" } },
        { id: "trigger", name: "Trigger", type: "trigger", ui_properties: { position: "left-bottom" } }
      ],
      outputs: [
        { id: "value", name: "Value", type: "any", ui_properties: { position: "right-top" } },
        { id: "completed", name: "Completed", type: "trigger", ui_properties: { position: "right-bottom" } }
      ],
      ui_properties: {
        color: "#3498db",
        icon: "database",
        width: 240
      }
    },
    {
      id: "core.get_variable",
      name: "Get Variable",
      category: "VARIABLES",
      description: "Get a variable value",
      inputs: [
        { id: "trigger", name: "Trigger", type: "trigger", ui_properties: { position: "left-top" } }
      ],
      outputs: [
        { id: "value", name: "Value", type: "any", ui_properties: { position: "right-top" } },
        { id: "exists", name: "Exists", type: "boolean", ui_properties: { position: "right-bottom" } }
      ],
      ui_properties: {
        color: "#2ecc71",
        icon: "database",
        width: 240
      }
    },
    {
      id: "core.text_input",
      name: "Text Input",
      category: "TEXT",
      description: "Enter text manually",
      inputs: [
        { id: "trigger", name: "Trigger", type: "trigger", ui_properties: { position: "left-top" } }
      ],
      outputs: [
        { id: "text", name: "Text", type: "string", ui_properties: { position: "right-top" } },
        { id: "length", name: "Length", type: "number", ui_properties: { position: "right-center" } }
      ],
      ui_properties: {
        color: "#3498db",
        icon: "font",
        width: 240
      }
    },
    {
      id: "core.text_output",
      name: "Text Output",
      category: "TEXT",
      description: "Display text results",
      inputs: [
        { id: "text", name: "Text", type: "string", required: true, ui_properties: { position: "left-top" } },
        { id: "trigger", name: "Trigger", type: "trigger", ui_properties: { position: "left-bottom" } }
      ],
      outputs: [
        { id: "text", name: "Text", type: "string", ui_properties: { position: "right-top" } }
      ],
      ui_properties: {
        color: "#e74c3c",
        icon: "comment",
        width: 240
      }
    },
    {
      id: "core.conditional",
      name: "Conditional",
      category: "CONTROL_FLOW",
      description: "Branch workflow based on conditions",
      inputs: [
        { id: "condition", name: "Condition", type: "boolean", required: true, ui_properties: { position: "left-top" } },
        { id: "trigger", name: "Trigger", type: "trigger", required: true, ui_properties: { position: "left-bottom" } }
      ],
      outputs: [
        { id: "true_branch", name: "True", type: "trigger", ui_properties: { position: "right-top" } },
        { id: "false_branch", name: "False", type: "trigger", ui_properties: { position: "right-bottom" } }
      ],
      ui_properties: {
        color: "#e67e22",
        icon: "code-branch",
        width: 240
      }
    },
    {
      id: "core.switch",
      name: "Switch",
      category: "CONTROL_FLOW",
      description: "Multi-way branching based on a value",
      inputs: [
        { id: "value", name: "Value", type: "any", required: true, ui_properties: { position: "left-top" } },
        { id: "cases", name: "Cases", type: "array", ui_properties: { position: "left-center" } },
        { id: "trigger", name: "Trigger", type: "trigger", required: true, ui_properties: { position: "left-bottom" } }
      ],
      outputs: [
        { id: "case_1", name: "Case 1", type: "trigger", ui_properties: { position: "right-top" } },
        { id: "case_2", name: "Case 2", type: "trigger", ui_properties: { position: "right-center" } },
        { id: "default", name: "Default", type: "trigger", ui_properties: { position: "right-bottom" } },
        { id: "selected_case", name: "Selected Case", type: "string", ui_properties: { position: "right-bottom" } }
      ],
      ui_properties: {
        color: "#9b59b6",
        icon: "random",
        width: 240
      }
    },
    {
      id: "core.delay",
      name: "Delay",
      category: "UTILITIES",
      description: "Delay execution for a specified time",
      inputs: [
        { id: "duration", name: "Duration (ms)", type: "number", required: true, ui_properties: { position: "left-top" } },
        { id: "trigger", name: "Trigger", type: "trigger", required: true, ui_properties: { position: "left-bottom" } }
      ],
      outputs: [
        { id: "completed", name: "Completed", type: "trigger", ui_properties: { position: "right-top" } }
      ],
      ui_properties: {
        color: "#34495e",
        icon: "clock",
        width: 240
      }
    },
    {
      id: "core.random_generator",
      name: "Random Generator",
      category: "UTILITIES",
      description: "Generate random values",
      inputs: [
        { id: "min", name: "Min", type: "number", ui_properties: { position: "left-top" } },
        { id: "max", name: "Max", type: "number", ui_properties: { position: "left-center" } },
        { id: "type", name: "Type", type: "string", ui_properties: { position: "left-center" } },
        { id: "trigger", name: "Trigger", type: "trigger", ui_properties: { position: "left-bottom" } }
      ],
      outputs: [
        { id: "value", name: "Value", type: "any", ui_properties: { position: "right-top" } },
        { id: "completed", name: "Completed", type: "trigger", ui_properties: { position: "right-bottom" } }
      ],
      ui_properties: {
        color: "#1abc9c",
        icon: "dice",
        width: 240
      }
    },
    {
      id: "core.http_request",
      name: "HTTP Request",
      category: "WEB_API",
      description: "Make HTTP requests to external APIs",
      inputs: [
        { id: "url", name: "URL", type: "string", required: true, ui_properties: { position: "left-top" } },
        { id: "method", name: "Method", type: "string", ui_properties: { position: "left-center" } },
        { id: "headers", name: "Headers", type: "object", ui_properties: { position: "left-center" } },
        { id: "body", name: "Body", type: "any", ui_properties: { position: "left-bottom" } },
        { id: "trigger", name: "Trigger", type: "trigger", ui_properties: { position: "left-bottom" } }
      ],
      outputs: [
        { id: "response", name: "Response", type: "any", ui_properties: { position: "right-top" } },
        { id: "status", name: "Status", type: "number", ui_properties: { position: "right-center" } },
        { id: "error", name: "Error", type: "string", ui_properties: { position: "right-bottom" } },
        { id: "completed", name: "Completed", type: "trigger", ui_properties: { position: "right-bottom" } }
      ],
      ui_properties: {
        color: "#3498db",
        icon: "globe",
        width: 240
      }
    }
  ],
  plugins: [
    {
      id: "http_request",
      name: "HTTP Request",
      category: "WEB_API",
      description: "Make HTTP requests to external APIs",
      inputs: [
        { id: "url", name: "URL", type: "string", required: true, ui_properties: { position: "left-top" } },
        { id: "method", name: "Method", type: "string", ui_properties: { position: "left-center" } },
        { id: "headers", name: "Headers", type: "object", ui_properties: { position: "left-center" } },
        { id: "body", name: "Body", type: "any", ui_properties: { position: "left-bottom" } },
        { id: "trigger", name: "Trigger", type: "trigger", ui_properties: { position: "left-bottom" } }
      ],
      outputs: [
        { id: "response", name: "Response", type: "any", ui_properties: { position: "right-top" } },
        { id: "status", name: "Status", type: "number", ui_properties: { position: "right-center" } },
        { id: "error", name: "Error", type: "string", ui_properties: { position: "right-bottom" } }
      ],
      ui_properties: {
        color: "#e74c3c",
        icon: "globe",
        width: 240
      }
    },
    {
      id: "json_parser",
      name: "JSON Parser",
      category: "DATA",
      description: "Parse and stringify JSON data",
      inputs: [
        { id: "input", name: "Input", type: "string", required: true, ui_properties: { position: "left-top" } },
        { id: "trigger", name: "Trigger", type: "trigger", ui_properties: { position: "left-bottom" } }
      ],
      outputs: [
        { id: "output", name: "Output", type: "object", ui_properties: { position: "right-top" } },
        { id: "error", name: "Error", type: "string", ui_properties: { position: "right-bottom" } }
      ],
      ui_properties: {
        color: "#3498db",
        icon: "code",
        width: 240
      }
    },
    {
      id: "csv_parser",
      name: "CSV Parser",
      category: "DATA",
      description: "Parse and format CSV data",
      inputs: [
        { id: "input", name: "Input", type: "string", required: true, ui_properties: { position: "left-top" } },
        { id: "has_header", name: "Has Header", type: "boolean", ui_properties: { position: "left-center" } },
        { id: "delimiter", name: "Delimiter", type: "string", ui_properties: { position: "left-center" } },
        { id: "trigger", name: "Trigger", type: "trigger", ui_properties: { position: "left-bottom" } }
      ],
      outputs: [
        { id: "output", name: "Output", type: "array", ui_properties: { position: "right-top" } },
        { id: "headers", name: "Headers", type: "array", ui_properties: { position: "right-center" } },
        { id: "error", name: "Error", type: "string", ui_properties: { position: "right-bottom" } }
      ],
      ui_properties: {
        color: "#2ecc71",
        icon: "table",
        width: 240
      }
    }
  ]
};

/**
 * Mock type system
 */
export const mockTypeSystem = {
  types: {
    "string": {
      description: "A text value",
      ui_properties: {
        color: "#60a5fa",
        icon: "font"
      }
    },
    "number": {
      description: "A numeric value",
      ui_properties: {
        color: "#a78bfa",
        icon: "hashtag"
      }
    },
    "boolean": {
      description: "A true/false value",
      ui_properties: {
        color: "#f87171",
        icon: "toggle-on"
      }
    },
    "object": {
      description: "A JavaScript object",
      ui_properties: {
        color: "#4ade80",
        icon: "cube"
      }
    },
    "array": {
      description: "An array of values",
      ui_properties: {
        color: "#fbbf24",
        icon: "list"
      }
    },
    "any": {
      description: "Any type of value",
      ui_properties: {
        color: "#9ca3af",
        icon: "asterisk"
      }
    },
    "trigger": {
      description: "A workflow trigger signal",
      ui_properties: {
        color: "#ec4899",
        icon: "bolt"
      }
    }
  },
  rules: [
    { source: "string", target: ["string", "any"], bidirectional: false },
    { source: "number", target: ["number", "string", "any"], bidirectional: false },
    { source: "boolean", target: ["boolean", "string", "any"], bidirectional: false },
    { source: "object", target: ["object", "any"], bidirectional: false },
    { source: "array", target: ["array", "any"], bidirectional: false },
    { source: "trigger", target: ["trigger"], bidirectional: true },
    { source: "any", target: ["string", "number", "boolean", "object", "array", "any"], bidirectional: true }
  ]
};
