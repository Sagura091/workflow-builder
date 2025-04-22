# Organizing Plugins and Core Nodes

This directory contains scripts to automatically organize plugins and core nodes in the workflow builder backend.

## What the Script Does

The `organize_nodes.py` script will:

1. Identify duplicate files between plugins and core_nodes
2. Move plugins to their appropriate category directories
3. Remove duplicates from the root plugins directory
4. Organize core nodes according to the registry in `config/core_nodes_registry.json`
5. Update the registry with any new core nodes found
6. Create necessary `__init__.py` files

## How to Run the Script

### Windows

1. Open a command prompt in the backend directory
2. Run `organize_nodes.bat`

Or simply double-click on `organize_nodes.bat` in File Explorer.

### Unix/Linux/Mac

1. Open a terminal in the backend directory
2. Make the script executable: `chmod +x organize_nodes.sh`
3. Run the script: `./organize_nodes.sh`

### Directly with Python

1. Open a terminal or command prompt in the backend directory
2. Run `python organize_nodes.py`

## Categories

### Plugin Categories

- **text_processing**: Plugins for text processing (text analysis, text splitting, etc.)
- **data_handling**: Plugins for data manipulation (filtering, mapping, sorting, etc.)
- **web_api**: Plugins for interacting with web APIs
- **file_operations**: Plugins for file operations
- **control_flow**: Advanced control flow plugins

### Core Node Categories

- **control_flow**: Nodes for controlling the flow of execution (begin, end, conditional, loop, switch)
- **data**: Nodes for basic data manipulation (object properties, variable)
- **file_storage**: Nodes for reading and writing files
- **math**: Nodes for mathematical operations
- **text**: Nodes for text processing
- **utilities**: Utility nodes (delay, trigger)
- **web_api**: Nodes for interacting with web APIs

## Duplicates

The script will identify and handle duplicates between plugins and core nodes. By default, it will keep the core node version and remove the plugin version for the following files:

- conditional.py
- data_merger.py
- file_reader.py
- http_request.py
- loop.py
- input_text.py
- output_text.py

## Core Nodes Registry

The script uses a registry file (`config/core_nodes_registry.json`) to track all core nodes and their categories. This registry ensures that core nodes are consistently organized and categorized.

The registry contains the following information for each core node:

- `id`: The unique identifier for the node (e.g., "core.begin")
- `file`: The filename of the node (e.g., "begin.py")
- `category`: The category the node belongs to (e.g., "control_flow")
- `description`: A brief description of the node

When the script runs, it will:

1. Check if each core node is in the registry
2. If found, use the category from the registry
3. If not found, determine the category based on the file content and add it to the registry
4. Update the registry with any new nodes

This ensures that all core nodes are properly categorized and tracked.

## Customization

If you need to customize the script's behavior, you can edit the following variables in `organize_nodes.py`:

- `PLUGIN_CATEGORIES`: Keywords used to categorize plugins
- `CORE_NODE_CATEGORIES`: Keywords used to categorize core nodes
- `KEEP_IN_ROOT`: Files to keep in the root plugins directory
- `DUPLICATES_TO_REMOVE`: Duplicate files to remove from plugins

You can also directly edit the `core_nodes_registry.json` file to change the categories of specific core nodes.
