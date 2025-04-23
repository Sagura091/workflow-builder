# Workflow Builder Demo Mode

This is a standalone demo of the Workflow Builder UI that allows users to explore the interface and functionality without needing to set up a backend server.

## How to Run the Demo

There are several ways to access the demo:

1. **Local Development Server**:
   ```
   npm start
   ```
   The demo mode is automatically enabled when running on localhost.

2. **URL Parameter**:
   Add `?demo=true` to any URL to enable demo mode.

3. **Demo Hostname**:
   Any hostname that includes "demo" will automatically enable demo mode.

4. **Environment Variable**:
   Set `REACT_APP_DEMO_MODE=true` in your environment to enable demo mode.

## Demo Features

The demo includes the following features:

- **Sample Workflow**: The demo starts with a pre-configured sample workflow to demonstrate the UI.
- **Node Library**: Browse and add nodes from various categories.
- **Node Configuration**: Configure node properties by clicking on them.
- **Canvas Navigation**: Pan, zoom, and center the canvas.
- **Node Connections**: Create connections between nodes by dragging from output to input points.
- **Execution Simulation**: Execute the workflow to see simulated results.
- **Keyboard Shortcuts**: Use keyboard shortcuts for common actions.
- **Feedback Collection**: Provide feedback on the UI through the feedback button.

## Keyboard Shortcuts

- **Scroll Wheel**: Zoom in/out
- **Alt+Click** or **Middle-Click**: Pan the canvas
- **C**: Center view
- **Ctrl+F** or **/** (slash): Search nodes
- **Alt+M**: Toggle minimap
- **Right-Click**: Open context menu

## Limitations

- The demo runs entirely in the browser with no backend connection.
- Workflows are not saved between sessions.
- Execution results are simulated and not based on actual processing.

## Feedback

We'd love to hear your thoughts on the Workflow Builder UI! Use the feedback button in the demo to share your experience, suggestions, or report issues.

## Development

The demo mode is implemented using React context to provide mock data and simulated functionality. The key components are:

- `DemoModeContext.tsx`: Manages the demo state and provides mock data.
- `mockData.ts`: Contains mock node types, plugins, and execution results.
- `DemoApp.tsx`: Standalone application component for the demo.

To modify the demo:

1. Edit `mockData.ts` to change the available node types or sample workflow.
2. Update `DemoModeContext.tsx` to modify the demo behavior.
3. Customize `DemoWelcomeModal.tsx` to change the welcome message.
