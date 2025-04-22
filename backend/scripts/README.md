# Scripts

This directory contains utility scripts for the Workflow Builder backend.

## Available Scripts

- `generate_node_metadata.py`: Generates metadata for nodes
- `organize_nodes.py`: Organizes nodes into categories
- `test_node_connections.py`: Tests node connections
- `test_node_execution.py`: Tests node execution
- `test_routes.py`: Tests API routes

## How to Run

### Windows

1. Open a command prompt in the backend directory
2. Run `python scripts/script_name.py`

### Unix/Linux/Mac

1. Open a terminal in the backend directory
2. Run `python scripts/script_name.py`

## Development

When adding new scripts, please follow these guidelines:

1. Add a docstring at the top of the script explaining its purpose
2. Add a `main()` function that contains the script's logic
3. Add a `if __name__ == "__main__":` block that calls the `main()` function
4. Update this README.md file with information about the new script
