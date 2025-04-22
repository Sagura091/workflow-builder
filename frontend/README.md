# Workflow Builder React TypeScript Frontend

This is a React TypeScript implementation of the Workflow Builder, designed to connect with the backend API for dynamic node generation and workflow execution.

## Features

- Drag and drop interface for building workflows
- Dynamic node configuration
- Connection management between nodes
- Workflow execution and monitoring
- Zoom and pan canvas navigation
- Minimap for large workflows
- Undo/redo functionality
- Backend integration for plugins

## Getting Started

### Prerequisites

- Node.js (v14 or later)
- npm or yarn
- Backend server running (see backend README)

### Installation

1. Install dependencies:

```bash
npm install
# or
yarn install
```

2. Start the development server:

```bash
npm start
# or
yarn start
```

The application will be available at http://localhost:3000 and will proxy API requests to the backend server at http://localhost:8000.

## Project Structure

- `src/components/WorkflowBuilder/` - Main workflow builder components
  - `index.tsx` - Main workflow builder component
  - `WorkflowCanvas.tsx` - Canvas for nodes and connections
  - `Node.tsx` - Individual node component
  - `ComponentSidebar.tsx` - Sidebar with available components
  - `CanvasControls.tsx` - Zoom, pan, and other canvas controls
  - `Minimap.tsx` - Minimap for canvas navigation
  - `NodeEditorModal.tsx` - Modal for editing node configuration
  - `ExecutionPanel.tsx` - Panel for workflow execution and monitoring
  - `WorkflowHeader.tsx` - Header with workflow actions

- `src/services/` - API services
  - `api.ts` - API client for backend communication

- `src/types/` - TypeScript type definitions
  - `index.ts` - Type definitions for nodes, connections, plugins, etc.

## Backend Integration

The frontend connects to the backend API to:

1. Fetch available plugins
2. Execute workflows
3. Save and load workflows

The API client is configured in `src/services/api.ts` and uses axios for HTTP requests.

## Customization

### Adding New Node Types

To add new node types, update the `nodeTypes` object in the appropriate components or create a new file for node type definitions.

### Styling

The application uses Tailwind CSS for styling. You can customize the appearance by modifying the CSS classes or updating the Tailwind configuration in `tailwind.config.js`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
