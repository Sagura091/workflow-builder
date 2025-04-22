import { getCoreNodes, getPlugins, validateNodeDefinition } from './api';
import { NodeTypeDefinition } from '../contexts/NodeTypesContext';

// Node status types
export type NodeStatus = 'available' | 'error' | 'deprecated' | 'experimental';

export interface DiscoveredNode extends NodeTypeDefinition {
  status: NodeStatus;
  statusMessage?: string;
  category: string;
  isCore: boolean;
}

/**
 * Service for discovering and validating available nodes
 */
export class NodeDiscoveryService {
  private nodes: Map<string, DiscoveredNode> = new Map();
  private listeners: Array<() => void> = [];

  /**
   * Discover all available nodes from the backend
   */
  public async discoverNodes(): Promise<Map<string, DiscoveredNode>> {
    try {
      console.log('Discovering nodes...');

      // Clear existing nodes
      this.nodes.clear();

      // Fetch core nodes
      const coreNodes = await getCoreNodes();
      console.log('Core nodes response:', coreNodes);

      // Process core nodes
      if (Array.isArray(coreNodes)) {
        console.log(`Processing ${coreNodes.length} core nodes`);
        for (const node of coreNodes) {
          await this.processNode(node, true);
        }
      } else if (coreNodes && typeof coreNodes === 'object') {
        // Check if coreNodes has a 'coreNodes' property that is an array
        const coreNodesArray = (coreNodes as any).coreNodes;
        if (coreNodesArray && Array.isArray(coreNodesArray)) {
          console.log(`Processing ${coreNodesArray.length} core nodes from object`);
          for (const node of coreNodesArray) {
            await this.processNode(node, true);
          }
        }
      }

      // Fetch plugins
      const plugins = await getPlugins();
      console.log('Plugins response:', plugins);

      // Process plugins
      if (Array.isArray(plugins)) {
        console.log(`Processing ${plugins.length} plugins`);
        for (const plugin of plugins) {
          await this.processNode(plugin, false);
        }
      } else if (plugins && typeof plugins === 'object') {
        // Check if plugins has a 'plugins' property that is an array
        const pluginsArray = (plugins as any).plugins;
        if (pluginsArray && Array.isArray(pluginsArray)) {
          console.log(`Processing ${pluginsArray.length} plugins from object`);
          for (const plugin of pluginsArray) {
            await this.processNode(plugin, false);
          }
        } else {
          // Try to process plugins as an object with plugin IDs as keys
          const pluginEntries = Object.entries(plugins);
          if (pluginEntries.length > 0) {
            console.log(`Processing ${pluginEntries.length} plugins from entries`);
            for (const [id, plugin] of pluginEntries) {
              if (typeof plugin === 'object' && plugin !== null) {
                // Add the ID to the plugin object if it doesn't have one
                const pluginWithId = { id, ...(plugin as object) };
                await this.processNode(pluginWithId, false);
              }
            }
          }
        }
      }

      console.log(`Discovered ${this.nodes.size} total nodes`);
      console.log('Nodes by category:', this.getNodesByCategory());

      // Notify listeners
      this.notifyListeners();

      return this.nodes;
    } catch (error) {
      console.error('Error discovering nodes:', error);
      throw error;
    }
  }

  /**
   * Process a node definition and add it to the discovered nodes
   */
  private async processNode(node: any, isCore: boolean): Promise<void> {
    try {
      // Skip if node doesn't have an ID
      if (!node.id) {
        console.warn('Node without ID found, skipping:', node);
        return;
      }

      // Extract plugin metadata if available
      let nodeData = node;
      if (node.__plugin_meta__) {
        // This is a plugin with metadata
        nodeData = {
          ...node,
          ...node.__plugin_meta__,
          inputs: node.__plugin_meta__.inputs || [],
          outputs: node.__plugin_meta__.outputs || [],
          category: node.__plugin_meta__.category || 'Plugins'
        };
      }

      // Validate node definition
      const validationResult = await this.validateNode(nodeData);

      // Create discovered node
      const discoveredNode: DiscoveredNode = {
        ...nodeData,
        status: validationResult.valid ? 'available' : 'error',
        statusMessage: validationResult.message,
        category: nodeData.category || (isCore ? 'Core' : 'Plugins'),
        isCore
      };

      // Add to map
      this.nodes.set(node.id, discoveredNode);

      console.log(`Processed node: ${node.id}, category: ${discoveredNode.category}`);
    } catch (error) {
      console.error(`Error processing node ${node.id}:`, error);
    }
  }

  /**
   * Validate a node definition
   */
  private async validateNode(node: any): Promise<{ valid: boolean; message?: string }> {
    try {
      // Make a copy of the node to avoid modifying the original
      const nodeCopy = { ...node };

      // Basic validation
      if (!nodeCopy.id) {
        return { valid: false, message: 'Missing required field: id' };
      }

      // For backward compatibility, use title as name if name is not provided
      if (!nodeCopy.name && nodeCopy.title) {
        nodeCopy.name = nodeCopy.title;
      }

      if (!nodeCopy.name) {
        return { valid: false, message: 'Missing required field: name' };
      }

      // Ensure inputs and outputs are arrays
      if (!Array.isArray(nodeCopy.inputs)) {
        nodeCopy.inputs = [];
      }

      if (!Array.isArray(nodeCopy.outputs)) {
        nodeCopy.outputs = [];
      }

      // Fix input ports
      for (let i = 0; i < nodeCopy.inputs.length; i++) {
        const input = nodeCopy.inputs[i];

        // For backward compatibility, use name as id if id is not provided
        if (!input.id && input.name) {
          input.id = input.name;
        }

        // If still no id, generate one
        if (!input.id) {
          input.id = `input_${i}`;
        }

        // If no name, use id
        if (!input.name) {
          input.name = input.id;
        }

        // If no type, default to 'any'
        if (!input.type) {
          input.type = 'any';
        }
      }

      // Fix output ports
      for (let i = 0; i < nodeCopy.outputs.length; i++) {
        const output = nodeCopy.outputs[i];

        // For backward compatibility, use name as id if id is not provided
        if (!output.id && output.name) {
          output.id = output.name;
        }

        // If still no id, generate one
        if (!output.id) {
          output.id = `output_${i}`;
        }

        // If no name, use id
        if (!output.name) {
          output.name = output.id;
        }

        // If no type, default to 'any'
        if (!output.type) {
          output.type = 'any';
        }
      }

      // Set status to available if not provided
      if (!nodeCopy.status) {
        nodeCopy.status = 'available';
      }

      // Call backend validation if available
      try {
        const backendValidation = await validateNodeDefinition(nodeCopy);
        if (backendValidation && !backendValidation.valid) {
          return { valid: false, message: backendValidation.message };
        }

        // If backend validation returned an updated node definition, use it
        if (backendValidation && backendValidation.node_def) {
          Object.assign(node, backendValidation.node_def);
        } else {
          // Otherwise, apply our fixes to the original node
          Object.assign(node, nodeCopy);
        }
      } catch (error) {
        console.warn('Backend validation not available, using client-side validation only');
        // Apply our fixes to the original node
        Object.assign(node, nodeCopy);
      }

      return { valid: true };
    } catch (error) {
      return { valid: false, message: `Validation error: ${error}` };
    }
  }

  /**
   * Get all discovered nodes
   */
  public getNodes(): Map<string, DiscoveredNode> {
    return this.nodes;
  }

  /**
   * Get nodes by category
   */
  public getNodesByCategory(): Record<string, DiscoveredNode[]> {
    const categories: Record<string, DiscoveredNode[]> = {};

    this.nodes.forEach(node => {
      const category = node.category || (node.isCore ? 'Core' : 'Plugins');
      if (!categories[category]) {
        categories[category] = [];
      }
      categories[category].push(node);
    });

    return categories;
  }

  /**
   * Add a listener for node changes
   */
  public addListener(listener: () => void): () => void {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  /**
   * Notify all listeners of changes
   */
  private notifyListeners(): void {
    this.listeners.forEach(listener => listener());
  }
}

// Create singleton instance
export const nodeDiscoveryService = new NodeDiscoveryService();

// Export default instance
export default nodeDiscoveryService;
