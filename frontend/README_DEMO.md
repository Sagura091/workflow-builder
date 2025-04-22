# Workflow Builder Demo

Welcome to the Workflow Builder Demo! This is a live demo of the Workflow Builder application that runs entirely in your browser.

## Demo URL

You can access the live demo at:
```
https://Sagura091.github.io/workflow-builder
```

## Features

The demo includes all the UI features of the Workflow Builder:

- **Node Library**: Browse and add nodes from various categories
- **Canvas Navigation**: Pan, zoom, and center the canvas
- **Node Connections**: Create connections between nodes
- **Node Configuration**: Configure node properties
- **Search**: Find nodes by name or content
- **Keyboard Shortcuts**: Use keyboard shortcuts for common actions
- **Execution Simulation**: Execute the workflow to see simulated results

## How to Use

1. **Add Nodes**: Drag nodes from the left panel onto the canvas
2. **Connect Nodes**: Drag from an output point to an input point to create connections
3. **Configure Nodes**: Click on a node to configure its properties
4. **Navigate the Canvas**:
   - Use the mouse wheel to zoom in/out
   - Hold Alt+Click or Middle-Click to pan the canvas
   - Press "C" to center the view
   - Press "Ctrl+F" or "/" to search for nodes
   - Right-click for context menu options

## Keyboard Shortcuts

- **Scroll Wheel**: Zoom in/out
- **Alt+Click** or **Middle-Click**: Pan the canvas
- **C**: Center view
- **Ctrl+F** or **/** (slash): Search nodes
- **Alt+M**: Toggle minimap
- **Right-Click**: Open context menu

## Limitations

Since this is a demo without a backend:

- Workflows are not saved between sessions
- Execution results are simulated
- Some advanced features may be limited

## Feedback

We'd love to hear your thoughts on the Workflow Builder! Use the feedback button in the demo to share your experience, suggestions, or report issues.

## Source Code

The source code for this demo is available on GitHub:
```
https://github.com/Sagura091/workflow-builder
```

## Local Development

If you want to run the demo locally:

1. Clone the repository
2. Navigate to the frontend directory
3. Run `npm install` to install dependencies
4. Run `npm start` to start the development server
5. Open `http://localhost:3000` in your browser

## Deploying Your Own Version

If you want to deploy your own version of the demo:

1. Fork the repository
2. Update the `homepage` field in `package.json` to match your GitHub username
3. Run the deployment script (`deploy-demo.bat` or `deploy-demo.ps1`)
4. Your demo will be available at `https://yourusername.github.io/workflow-builder`
