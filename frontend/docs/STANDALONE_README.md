# Workflow Builder Standalone Demo

This is a standalone HTML file version of the Workflow Builder demo that can be opened directly in a web browser without any installation or setup.

## How to Use

1. **Open the HTML file**: Simply double-click on the `workflow-builder-demo.html` file to open it in your default web browser.

2. **No installation required**: The demo runs entirely in your browser with no backend dependencies.

3. **Try out the features**:
   - Drag nodes from the left panel onto the canvas
   - Connect nodes by dragging from output to input points
   - Configure nodes by clicking on them
   - Use the mouse wheel to zoom in/out
   - Pan the canvas by holding Alt+Click or Middle-Click
   - Press "C" to center the view
   - Press "Ctrl+F" or "/" to search for nodes
   - Right-click for context menu options

## Features

The standalone demo includes all the UI features of the Workflow Builder:

- **Node Library**: Browse and add nodes from various categories
- **Canvas Navigation**: Pan, zoom, and center the canvas
- **Node Connections**: Create connections between nodes
- **Node Configuration**: Configure node properties
- **Search**: Find nodes by name or content
- **Keyboard Shortcuts**: Use keyboard shortcuts for common actions
- **Execution Simulation**: Execute the workflow to see simulated results

## Limitations

Since this is a standalone demo without a backend:

- Workflows are not saved between sessions
- Execution results are simulated
- Some advanced features may be limited

## Sharing the Demo

You can easily share the Workflow Builder demo with others:

1. Send them the HTML file via email or file sharing
2. They can open it directly in their browser without installing anything
3. It works offline - no internet connection required after the initial load

## Providing Feedback

We'd love to hear your thoughts on the Workflow Builder! Use the "Send Feedback" button in the demo footer to share your experience, suggestions, or report issues.

## Creating Your Own Standalone Demo

To create your own standalone demo HTML file:

1. Clone the repository
2. Run `npm install` to install dependencies
3. Run `npm run create-standalone` to generate the standalone HTML file
4. The file will be created at `build/workflow-builder-demo.html`

## Technical Details

The standalone HTML file:

- Contains all necessary JavaScript and CSS bundled together
- Includes all dependencies (React, ReactDOM, etc.)
- Has all images converted to base64 and embedded
- Forces demo mode to be enabled
- Simulates backend responses with mock data
