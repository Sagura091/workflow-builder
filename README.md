# Workflow Builder

A powerful, visual workflow builder for creating, managing, and executing workflows with a node-based interface. This tool allows users to design complex workflows by connecting nodes that represent different operations, from basic data processing to advanced AI and machine learning tasks.

![Workflow Builder Demo](https://user-images.githubusercontent.com/placeholder/workflow-builder-demo.png)

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Components](#components)
  - [Frontend](#frontend)
  - [Backend](#backend)
  - [Core Nodes](#core-nodes)
  - [Plugins](#plugins)
  - [Type System](#type-system)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [Usage](#usage)
  - [Creating Workflows](#creating-workflows)
  - [Executing Workflows](#executing-workflows)
  - [Saving and Loading](#saving-and-loading)
- [Development](#development)
  - [Adding Core Nodes](#adding-core-nodes)
  - [Creating Plugins](#creating-plugins)
  - [Extending the Type System](#extending-the-type-system)
- [Deployment](#deployment)
- [API Reference](#api-reference)
- [Acronyms and Terminology](#acronyms-and-terminology)
- [Contributing](#contributing)
- [License](#license)

## Overview

Workflow Builder is a visual programming environment that enables users to create workflows by connecting nodes on a canvas. Each node represents a specific operation, and connections between nodes define the flow of data. This approach makes complex processes accessible to users without requiring extensive programming knowledge.

The application follows a Model-View-Controller (MVC) architecture with a React frontend and a FastAPI backend. It supports a plugin system for extensibility and a type system for validating connections between nodes.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Workflow Builder                         │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                           Frontend (React)                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐    │
│  │ Node Library │   │ Canvas      │   │ Properties Panel    │    │
│  └─────────────┘   └─────────────┘   └─────────────────────┘    │
│                                                                  │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐    │
│  │ Execution   │   │ Search      │   │ Keyboard Shortcuts  │    │
│  │ Panel       │   │ Interface   │   │                     │    │
│  └─────────────┘   └─────────────┘   └─────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Backend (FastAPI)                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐    │
│  │ Core Nodes  │   │ Plugins     │   │ Type System         │    │
│  └─────────────┘   └─────────────┘   └─────────────────────┘    │
│                                                                  │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐    │
│  │ Workflow    │   │ Execution   │   │ Authentication      │    │
│  │ Management  │   │ Engine      │   │                     │    │
│  └─────────────┘   └─────────────┘   └─────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **Visual Workflow Builder**: Drag-and-drop interface for creating workflows
- **Node-Based System**: Connect nodes to create complex data flows
- **Real-Time Execution**: Execute workflows and see results in real-time
- **Type System**: Validate connections between nodes based on data types
- **Plugin Architecture**: Extend functionality with custom plugins
- **Core Nodes**: Built-in nodes for common operations
- **Responsive Design**: Works on desktop and tablet devices
- **Keyboard Shortcuts**: Efficient workflow creation with keyboard shortcuts
- **Search Functionality**: Quickly find nodes by name or functionality
- **Customizable UI**: Dark mode, theme customization, and layout options
- **Standalone Demo**: Share workflows as standalone HTML files

## Components

### Frontend

The frontend is built with React and TypeScript, providing a responsive and interactive user interface for creating and managing workflows.

#### Key Components:

- **WorkflowBuilder**: The main component that orchestrates the entire UI
- **WorkflowCanvas**: The canvas where nodes are placed and connected
- **NodeLibrary**: A panel displaying available nodes categorized by function
- **PropertiesPanel**: A panel for configuring selected nodes
- **ExecutionPanel**: Controls for executing workflows and viewing results
- **NodeEditorModal**: A modal for detailed node configuration
- **KeyboardShortcutsModal**: A modal displaying available keyboard shortcuts

#### Context Providers:

- **NodeTypesProvider**: Provides information about available node types
- **NodeDiscoveryProvider**: Discovers and categorizes available nodes
- **NodeConfigProvider**: Manages node configurations
- **WebSocketProvider**: Handles real-time communication with the backend
- **DemoModeProvider**: Manages the demo mode functionality
- **ThemeProvider**: Manages UI themes and appearance settings

### Backend

The backend is built with FastAPI, providing a fast and efficient API for executing workflows, managing plugins, and handling the type system.

#### Key Components:

- **API Routes**: RESTful endpoints for interacting with the application
- **Workflow Engine**: Executes workflows by processing nodes in the correct order
- **Plugin Manager**: Loads and manages plugins
- **Type System**: Validates connections between nodes based on data types
- **Authentication**: Handles user authentication and authorization
- **WebSocket Server**: Provides real-time updates during workflow execution

### Core Nodes

Core nodes are built-in nodes that provide essential functionality for creating workflows. They are organized into categories based on their function.

#### Categories:

1. **Basic Flow Control**
   - Begin: Starting point for workflows
   - End: Endpoint for workflows
   - Branch: Conditional branching
   - Merge: Combine multiple paths
   - Loop: Iterate over data

2. **Data Handling**
   - Variable: Store and retrieve data
   - Array: Create and manipulate arrays
   - Object: Create and manipulate objects
   - Transform: Convert data between formats

3. **Text Processing**
   - Text Input: Enter text data
   - Text Output: Display text data
   - Text Manipulation: Modify text (concat, split, replace, etc.)
   - Regex: Regular expression operations

4. **Math & Logic**
   - Math Operations: Basic arithmetic operations
   - Comparison: Compare values
   - Logical Operations: AND, OR, NOT operations
   - Statistical Functions: Mean, median, mode, etc.

5. **File & Data Storage**
   - File Read: Read data from files
   - File Write: Write data to files
   - CSV Processing: Work with CSV files
   - JSON Processing: Work with JSON files

6. **Web & API**
   - HTTP Request: Make HTTP requests
   - API Integration: Connect to external APIs
   - WebSocket: Real-time communication
   - HTML Parsing: Extract data from HTML

7. **Utilities**
   - Delay: Introduce delays in workflow execution
   - Log: Log messages for debugging
   - Error Handling: Handle and recover from errors
   - Comment: Add notes to workflows

### Plugins

Plugins extend the functionality of the Workflow Builder by adding new nodes, types, or integrations. They are loaded dynamically by the backend and made available to the frontend.

#### Plugin Structure:

```
plugin/
├── __init__.py           # Plugin initialization
├── metadata.json         # Plugin metadata
├── nodes/                # Custom nodes
│   ├── node1.py
│   └── node2.py
├── types/                # Custom types
│   └── custom_types.json
└── assets/               # Plugin assets
    ├── icons/
    └── documentation/
```

#### Plugin Metadata:

```json
{
  "name": "Example Plugin",
  "version": "1.0.0",
  "description": "An example plugin for Workflow Builder",
  "author": "Your Name",
  "website": "https://example.com",
  "category": "Utilities",
  "dependencies": [],
  "nodes": [
    {
      "id": "example.node1",
      "name": "Example Node 1",
      "description": "An example node",
      "inputs": [
        {
          "name": "input1",
          "type": "string",
          "description": "Input 1"
        }
      ],
      "outputs": [
        {
          "name": "output1",
          "type": "string",
          "description": "Output 1"
        }
      ],
      "configFields": [
        {
          "name": "config1",
          "type": "string",
          "default": "",
          "description": "Configuration 1"
        }
      ]
    }
  ]
}
```

### Type System

The type system validates connections between nodes based on data types. It ensures that the output of one node is compatible with the input of another node.

#### Type Hierarchy:

```
any
├── string
│   ├── email
│   ├── url
│   └── path
├── number
│   ├── integer
│   └── float
├── boolean
├── array
│   └── typed_array<T>
├── object
│   └── typed_object<T>
├── null
└── custom_types...
```

#### Type Compatibility Rules:

- A type is always compatible with itself
- A type is compatible with its parent types
- A type may be compatible with other types based on conversion rules
- The `any` type is compatible with all types

## Getting Started

### Prerequisites

- Node.js (v14 or later)
- Python (v3.8 or later)
- npm or yarn

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Sagura091/workflow-builder.git
   cd workflow-builder
   ```

2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

3. Install backend dependencies:
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the backend:
   ```bash
   cd backend
   python main.py
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000`

## Usage

### Creating Workflows

1. **Add Nodes**: Drag nodes from the Node Library to the canvas
2. **Connect Nodes**: Click and drag from an output port to an input port to create a connection
3. **Configure Nodes**: Click on a node to open its configuration panel
4. **Organize Workflow**: Arrange nodes on the canvas for clarity

### Executing Workflows

1. **Validate Workflow**: Check for errors in the workflow
2. **Execute Workflow**: Click the "Execute" button to run the workflow
3. **View Results**: See the results in the Execution Panel
4. **Debug Workflow**: Use the Log node to debug your workflow

### Saving and Loading

1. **Save Workflow**: Click the "Save" button to save your workflow
2. **Load Workflow**: Click the "Load" button to load a saved workflow
3. **Export Workflow**: Export your workflow as a JSON file
4. **Import Workflow**: Import a workflow from a JSON file

## Development

### Adding Core Nodes

1. Create a new Python file in the `backend/core_nodes` directory:
   ```python
   # backend/core_nodes/my_category/my_node.py
   from workflow_engine.node import Node

   class MyNode(Node):
       def __init__(self):
           super().__init__(
               id="my_category.my_node",
               name="My Node",
               category="My Category",
               description="A custom core node",
               inputs=[
                   {"name": "input1", "type": "string", "description": "Input 1"}
               ],
               outputs=[
                   {"name": "output1", "type": "string", "description": "Output 1"}
               ],
               config_fields=[
                   {"name": "config1", "type": "string", "default": "", "description": "Configuration 1"}
               ]
           )

       def execute(self, inputs, config):
           # Process inputs and config
           result = inputs["input1"] + " " + config["config1"]
           # Return outputs
           return {"output1": result}
   ```

2. Register the node in `backend/core_nodes/__init__.py`:
   ```python
   from .my_category.my_node import MyNode

   def register_nodes(registry):
       registry.register(MyNode())
   ```

### Creating Plugins

1. Create a new directory in the `backend/plugins` directory:
   ```
   backend/plugins/my_plugin/
   ```

2. Create the plugin metadata file:
   ```json
   // backend/plugins/my_plugin/metadata.json
   {
     "name": "My Plugin",
     "version": "1.0.0",
     "description": "A custom plugin",
     "author": "Your Name",
     "category": "Utilities",
     "nodes": [
       {
         "id": "my_plugin.my_node",
         "name": "My Plugin Node",
         "description": "A custom plugin node",
         "inputs": [
           {
             "name": "input1",
             "type": "string",
             "description": "Input 1"
           }
         ],
         "outputs": [
           {
             "name": "output1",
             "type": "string",
             "description": "Output 1"
           }
         ],
         "configFields": [
           {
             "name": "config1",
             "type": "string",
             "default": "",
             "description": "Configuration 1"
           }
         ]
       }
     ]
   }
   ```

3. Create the plugin implementation:
   ```python
   # backend/plugins/my_plugin/__init__.py
   from workflow_engine.plugin import Plugin

   class MyPluginNode:
       def execute(self, inputs, config):
           # Process inputs and config
           result = inputs["input1"] + " " + config["config1"]
           # Return outputs
           return {"output1": result}

   class MyPlugin(Plugin):
       def __init__(self):
           super().__init__("my_plugin")

       def initialize(self):
           # Register nodes
           self.register_node("my_plugin.my_node", MyPluginNode())

       def shutdown(self):
           # Clean up resources
           pass
   ```

### Extending the Type System

1. Create a new type definition file:
   ```json
   // backend/types/my_types.json
   {
     "types": {
       "my_type": {
         "description": "A custom type",
         "parent": "string",
         "validators": [
           {
             "type": "regex",
             "pattern": "^my-[a-z]+$",
             "message": "Must start with 'my-' followed by lowercase letters"
           }
         ]
       }
     },
     "rules": [
       {
         "source": "my_type",
         "target": ["string"],
         "bidirectional": false
       }
     ]
   }
   ```

2. Register the type in the type system:
   ```python
   # backend/type_system/__init__.py
   def load_types():
       # Load built-in types
       # ...

       # Load custom types
       load_type_file("my_types.json")
   ```

## Directory Structure

The project is organized into the following directories:

```
workflow-builder/
├── backend/            # Backend code (FastAPI)
├── frontend/           # Frontend code (React)
├── docs/               # Documentation and examples
│   ├── examples/       # Example files and templates
│   └── json/           # JSON files for documentation and testing
├── scripts/            # Scripts for development and deployment
│   ├── deployment/     # Deployment scripts
│   └── utils/          # Utility scripts
└── backups/            # Backup files
```

## Deployment

### Deploying the Demo to GitHub Pages

1. Update the repository URL in `frontend/package.json`:
   ```json
   "homepage": "https://yourusername.github.io/workflow-builder"
   ```

2. Deploy to GitHub Pages using one of the deployment scripts:
   ```bash
   # On Windows
   ./scripts/deployment/deploy-github-pages.bat

   # On Unix/Linux/Mac
   ./scripts/deployment/deploy-github-pages.sh
   ```

3. The demo will be available at `https://yourusername.github.io/workflow-builder`

### Deploying the Full Application

1. Build the frontend:
   ```bash
   cd frontend
   npm run build
   ```

2. Set up the backend on your server:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Configure the backend to serve the frontend static files:
   ```python
   # backend/main.py
   from fastapi.staticfiles import StaticFiles

   app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="static")
   ```

4. Start the backend server:
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## API Reference

### Workflow API

- `GET /workflows`: Get all workflows
- `GET /workflows/{id}`: Get a specific workflow
- `POST /workflows`: Create a new workflow
- `PUT /workflows/{id}`: Update a workflow
- `DELETE /workflows/{id}`: Delete a workflow
- `POST /workflows/validate`: Validate a workflow
- `POST /workflows/execute`: Execute a workflow

### Node API

- `GET /core-nodes`: Get all core nodes
- `GET /core-nodes/categories`: Get all core node categories
- `GET /core-nodes/categories/{category}`: Get core nodes in a category
- `GET /core-nodes/{id}`: Get a specific core node
- `POST /nodes/validate`: Validate a node definition

### Plugin API

- `GET /plugins`: Get all plugins
- `GET /plugins/{id}`: Get a specific plugin
- `POST /plugins/{id}/enable`: Enable a plugin
- `POST /plugins/{id}/disable`: Disable a plugin

### Type System API

- `GET /type-system`: Get the type system
- `GET /type-system/compatibility`: Check type compatibility

## Acronyms and Terminology

- **API**: Application Programming Interface - A set of rules that allows different software applications to communicate with each other
- **CSS**: Cascading Style Sheets - A stylesheet language used for describing the presentation of a document written in HTML
- **DOM**: Document Object Model - A programming interface for web documents
- **HTML**: HyperText Markup Language - The standard markup language for documents designed to be displayed in a web browser
- **HTTP**: HyperText Transfer Protocol - An application protocol for distributed, collaborative, hypermedia information systems
- **JSON**: JavaScript Object Notation - A lightweight data-interchange format
- **MVC**: Model-View-Controller - A software design pattern commonly used for developing user interfaces
- **REST**: Representational State Transfer - An architectural style for designing networked applications
- **UI**: User Interface - The space where interactions between humans and machines occur
- **UX**: User Experience - The overall experience of a person using a product
- **WebSocket**: A communication protocol that provides full-duplex communication channels over a single TCP connection
- **YAML**: YAML Ain't Markup Language - A human-readable data serialization standard
- **JWT**: JSON Web Token - A compact, URL-safe means of representing claims to be transferred between two parties
- **SPA**: Single Page Application - A web application that interacts with the user by dynamically rewriting the current page
- **TypeScript**: A programming language developed and maintained by Microsoft, a strict syntactical superset of JavaScript
- **FastAPI**: A modern, fast web framework for building APIs with Python
- **React**: A JavaScript library for building user interfaces
- **Node.js**: A JavaScript runtime built on Chrome's V8 JavaScript engine

## Contributing

We welcome contributions to the Workflow Builder project! Please follow these steps to contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

Please make sure your code follows our coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
