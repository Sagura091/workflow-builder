import React, { useState, useMemo } from 'react';
import { useDrag } from 'react-dnd';
import { useNodeDiscovery } from '../../contexts/NodeDiscoveryContext';
import { DiscoveredNode, NodeStatus } from '../../services/nodeDiscovery';
import { mockNodeTypes } from '../../data/mockData';

interface NodeLibraryProps {
  onRefresh?: () => Promise<boolean> | void;
}

interface NodeItemProps {
  node: DiscoveredNode;
  isFavorite?: boolean;
  onToggleFavorite?: (nodeId: string) => void;
  onNodeUsed?: (nodeId: string) => void;
}

const NodeItem: React.FC<NodeItemProps> = ({ node, isFavorite = false, onToggleFavorite, onNodeUsed }) => {
  const [{ isDragging }, drag] = useDrag({
    type: 'component',
    item: { type: node.id },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
    end: (item, monitor) => {
      // If the drag was successful, add to recently used
      if (monitor.didDrop() && onNodeUsed) {
        onNodeUsed(node.id);
      }
    },
  });

  // Get status color
  const getStatusColor = (status: NodeStatus): string => {
    switch (status) {
      case 'available':
        return 'bg-green-100 text-green-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      case 'deprecated':
        return 'bg-yellow-100 text-yellow-800';
      case 'experimental':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get icon from UI properties or default
  const icon = node.ui_properties?.icon || 'cube';
  const color = node.ui_properties?.color || '#3b82f6';

  return (
    <div
      ref={drag}
      className={`component-item p-3 mb-2 rounded border border-gray-200 cursor-grab ${
        isDragging ? 'dragging' : ''
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center mr-3"
            style={{ backgroundColor: `${color}20` }}
          >
            <i className={`fas fa-${icon}`} style={{ color }}></i>
          </div>
          <div>
            <div className="font-medium">
              {node.name?.includes('.') ? node.name.split('.').pop() : (node.name || node.id?.split('.').pop() || 'Unknown')}
            </div>
            <div className="text-xs text-gray-500">{node.description}</div>
          </div>
        </div>
        <div className="flex items-center">
          {onToggleFavorite && (
            <button
              className="text-gray-400 hover:text-yellow-500 mr-2"
              onClick={(e) => {
                e.stopPropagation();
                onToggleFavorite(node.id);
              }}
              title={isFavorite ? "Remove from favorites" : "Add to favorites"}
            >
              <i className={`fas fa-star ${isFavorite ? 'text-yellow-500' : ''}`}></i>
            </button>
          )}
          <div className={`text-xs px-2 py-1 rounded-full ${getStatusColor(node.status)}`}>
            {node.status}
          </div>
        </div>
      </div>

      {/* Connection points preview */}
      <div className="flex justify-between mt-2 text-xs text-gray-500">
        <div>
          {node.inputs && node.inputs.length > 0 ? (
            <div className="flex items-center">
              <div className="w-2 h-2 rounded-full bg-blue-500 mr-1"></div>
              <span>{node.inputs.length} input{node.inputs.length !== 1 ? 's' : ''}</span>
            </div>
          ) : (
            <div className="flex items-center">
              <div className="w-2 h-2 rounded-full bg-gray-300 mr-1"></div>
              <span>No inputs</span>
            </div>
          )}
        </div>
        <div>
          {node.outputs && node.outputs.length > 0 ? (
            <div className="flex items-center">
              <span>{node.outputs.length} output{node.outputs.length !== 1 ? 's' : ''}</span>
              <div className="w-2 h-2 rounded-full bg-green-500 ml-1"></div>
            </div>
          ) : (
            <div className="flex items-center">
              <span>No outputs</span>
              <div className="w-2 h-2 rounded-full bg-gray-300 ml-1"></div>
            </div>
          )}
        </div>
      </div>

      {/* Show ports */}
      <div className="mt-2 text-xs">
        {node.inputs.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-1">
            {node.inputs.map(input => (
              <span
                key={input.id}
                className="px-2 py-1 rounded-full bg-blue-50 text-blue-700"
                title={`${input.name} (${input.type})`}
              >
                {input.name}
              </span>
            ))}
          </div>
        )}

        {node.outputs.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {node.outputs.map(output => (
              <span
                key={output.id}
                className="px-2 py-1 rounded-full bg-green-50 text-green-700"
                title={`${output.name} (${output.type})`}
              >
                {output.name}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Show error message if any */}
      {node.status === 'error' && node.statusMessage && (
        <div className="mt-2 text-xs text-red-600">
          <i className="fas fa-exclamation-triangle mr-1"></i>
          {node.statusMessage}
        </div>
      )}
    </div>
  );
};

// Create fallback nodes from mock data
const fallbackNodes: DiscoveredNode[] = [
  ...mockNodeTypes.coreNodes.map((node: any) => ({
    id: node.id,
    name: node.name,
    description: node.description || '',
    category: node.category || 'Core',
    status: 'available' as NodeStatus,
    statusMessage: '',
    isCore: true,
    inputs: node.inputs || [],
    outputs: node.outputs || [],
    ui_properties: node.ui_properties || {}
  })),
  ...mockNodeTypes.plugins.map((plugin: any) => ({
    id: plugin.id,
    name: plugin.name,
    description: plugin.description || '',
    category: plugin.category || 'Plugins',
    status: 'available' as NodeStatus,
    statusMessage: '',
    isCore: false,
    inputs: plugin.inputs || [],
    outputs: plugin.outputs || [],
    ui_properties: plugin.ui_properties || {}
  }))
];

const NodeLibrary: React.FC<NodeLibraryProps> = ({ onRefresh }) => {
  // Get node discovery context with fallback
  let nodesByCategory: Record<string, DiscoveredNode[]> = {};
  let loading = false;
  let error: string | null = null;
  let refreshNodes = async (): Promise<boolean> => { return true; };
  let allNodes: DiscoveredNode[] = [];

  try {
    const nodeDiscovery = useNodeDiscovery();
    nodesByCategory = nodeDiscovery.nodesByCategory;
    loading = nodeDiscovery.loading;
    error = nodeDiscovery.error;
    refreshNodes = nodeDiscovery.refreshNodes;
    allNodes = Array.from(nodeDiscovery.nodes.values());
  } catch (e) {
    console.warn('NodeDiscoveryProvider not available, using fallback values');
    error = 'Node discovery service not available';
  }
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [showOnlyAvailable, setShowOnlyAvailable] = useState(true);
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>({});
  const [favorites, setFavorites] = useState<string[]>(() => {
    const saved = localStorage.getItem('favoriteNodes');
    return saved ? JSON.parse(saved) : [];
  });
  const [recentlyUsed, setRecentlyUsed] = useState<string[]>(() => {
    const saved = localStorage.getItem('recentlyUsedNodes');
    return saved ? JSON.parse(saved) : [];
  });

  // Get available categories
  const categories = useMemo(() => {
    if (!nodesByCategory || Object.keys(nodesByCategory).length === 0) {
      console.warn('nodesByCategory is empty, using default categories');
      return ['CONTROL_FLOW', 'TEXT', 'DATA', 'MATH'];
    }
    return Object.keys(nodesByCategory).sort();
  }, [nodesByCategory]);

  // Handle refresh
  const handleRefresh = async () => {
    try {
      await refreshNodes();
      if (onRefresh) {
        onRefresh();
      }
    } catch (error) {
      console.error('Error refreshing nodes:', error);
    }
  };

  // Toggle favorite status for a node
  const toggleFavorite = (nodeId: string) => {
    const newFavorites = favorites.includes(nodeId)
      ? favorites.filter(id => id !== nodeId)
      : [...favorites, nodeId];

    setFavorites(newFavorites);
    localStorage.setItem('favoriteNodes', JSON.stringify(newFavorites));
  };

  // Add a node to recently used
  const addToRecentlyUsed = (nodeId: string) => {
    const newRecentlyUsed = [
      nodeId,
      ...recentlyUsed.filter(id => id !== nodeId).slice(0, 9) // Keep only 10 most recent
    ];

    setRecentlyUsed(newRecentlyUsed);
    localStorage.setItem('recentlyUsedNodes', JSON.stringify(newRecentlyUsed));
  };

  // Toggle category expansion
  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  // Filter nodes based on search term, category, and availability
  const getFilteredNodes = () => {
    // If nodesByCategory is empty, use fallback data
    if (!nodesByCategory || Object.keys(nodesByCategory).length === 0) {
      console.warn('No categories found, using fallback data');
      return fallbackNodes;
    }

    // If we have a search term, search across all categories
    if (searchTerm) {
      const result: DiscoveredNode[] = [];

      // Search in all nodes
      allNodes.forEach((node: DiscoveredNode) => {
        if (!node) return;

        // Filter by availability
        if (showOnlyAvailable && node.status !== 'available') {
          return;
        }

        // Filter by search term
        if (
          node.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          node.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          node.id?.toLowerCase().includes(searchTerm.toLowerCase())
        ) {
          result.push(node);
        }
      });

      return result;
    }

    // If we have a selected category, return nodes from that category
    if (selectedCategory) {
      const nodes = nodesByCategory[selectedCategory] || [];
      return nodes.filter(node => !showOnlyAvailable || node.status === 'available');
    }

    // Otherwise, return an empty array (we'll display by category)
    return [];
  };

  // Get favorite nodes
  const getFavoriteNodes = () => {
    return allNodes.filter(node =>
      favorites.includes(node.id) &&
      (!showOnlyAvailable || node.status === 'available')
    );
  };

  // Get recently used nodes
  const getRecentlyUsedNodes = () => {
    return recentlyUsed
      .map(id => allNodes.find(node => node.id === id))
      .filter(node => node && (!showOnlyAvailable || node.status === 'available')) as DiscoveredNode[];
  };

  return (
    <div className="component-sidebar p-4 bg-white border-r border-gray-200 overflow-y-auto">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Node Library</h2>
        <button
          className="text-blue-600 hover:text-blue-800"
          onClick={handleRefresh}
          disabled={loading}
          title="Refresh nodes"
        >
          <i className={`fas fa-sync ${loading ? 'animate-spin' : ''}`}></i>
        </button>
      </div>

      {/* Search */}
      <div className="mb-4">
        <div className="relative">
          <input
            type="text"
            className="w-full px-3 py-2 border border-gray-300 rounded-md pl-10"
            placeholder="Search nodes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <div className="absolute left-3 top-2.5 text-gray-400">
            <i className="fas fa-search"></i>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-4 flex flex-wrap gap-2">
        <button
          className={`px-3 py-1 text-sm rounded-full ${
            selectedCategory === null ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
          }`}
          onClick={() => setSelectedCategory(null)}
        >
          All
        </button>
        {categories.map(category => (
          <button
            key={category}
            className={`px-3 py-1 text-sm rounded-full ${
              selectedCategory === category ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
            }`}
            onClick={() => setSelectedCategory(category)}
          >
            {category}
          </button>
        ))}
      </div>

      {/* Show only available toggle */}
      <div className="mb-4 flex items-center">
        <label className="flex items-center cursor-pointer">
          <div className="relative">
            <input
              type="checkbox"
              className="sr-only"
              checked={showOnlyAvailable}
              onChange={() => setShowOnlyAvailable(!showOnlyAvailable)}
            />
            <div className={`w-10 h-5 ${showOnlyAvailable ? 'bg-blue-600' : 'bg-gray-200'} rounded-full shadow-inner`}></div>
            <div className={`absolute w-4 h-4 bg-white rounded-full shadow top-0.5 left-0.5 transition ${showOnlyAvailable ? 'transform translate-x-5' : ''}`}></div>
          </div>
          <div className="ml-3 text-sm">Show only available</div>
        </label>
      </div>

      {/* Error message */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-800 rounded">
          <i className="fas fa-exclamation-circle mr-2"></i>
          {error}
        </div>
      )}

      {/* Loading indicator */}
      {loading && (
        <div className="flex justify-center items-center p-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )}

      {/* Favorites section */}
      {!searchTerm && !selectedCategory && getFavoriteNodes().length > 0 && (
        <div className="mb-6">
          <div
            className="flex items-center justify-between cursor-pointer mb-2"
            onClick={() => toggleCategory('favorites')}
          >
            <h3 className="text-md font-semibold text-yellow-600">
              <i className="fas fa-star mr-2"></i>
              Favorites
            </h3>
            <i className={`fas fa-chevron-${expandedCategories['favorites'] ? 'down' : 'right'} text-gray-500`}></i>
          </div>

          {expandedCategories['favorites'] !== false && (
            <div className="pl-2">
              {getFavoriteNodes().map((node, index) => (
                <NodeItem
                  key={`favorite-${node.id}-${index}`}
                  node={node}
                  isFavorite={true}
                  onToggleFavorite={toggleFavorite}
                  onNodeUsed={addToRecentlyUsed}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Recently used section */}
      {!searchTerm && !selectedCategory && getRecentlyUsedNodes().length > 0 && (
        <div className="mb-6">
          <div
            className="flex items-center justify-between cursor-pointer mb-2"
            onClick={() => toggleCategory('recent')}
          >
            <h3 className="text-md font-semibold text-blue-600">
              <i className="fas fa-history mr-2"></i>
              Recently Used
            </h3>
            <i className={`fas fa-chevron-${expandedCategories['recent'] ? 'down' : 'right'} text-gray-500`}></i>
          </div>

          {expandedCategories['recent'] !== false && (
            <div className="pl-2">
              {getRecentlyUsedNodes().map((node, index) => (
                <NodeItem
                  key={`recent-${node.id}-${index}`}
                  node={node}
                  isFavorite={favorites.includes(node.id)}
                  onToggleFavorite={toggleFavorite}
                  onNodeUsed={addToRecentlyUsed}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Search results */}
      {(searchTerm || selectedCategory) && (
        <div>
          {getFilteredNodes().map((node, index) => (
            <NodeItem
              key={`search-${node.id}-${index}`}
              node={node}
              isFavorite={favorites.includes(node.id)}
              onToggleFavorite={toggleFavorite}
              onNodeUsed={addToRecentlyUsed}
            />
          ))}

          {/* Empty search results */}
          {!loading && getFilteredNodes().length === 0 && (
            <div className="text-center p-4 text-gray-500">
              <i className="fas fa-search text-3xl mb-2"></i>
              <p>No nodes found</p>
            </div>
          )}
        </div>
      )}

      {/* Categories */}
      {!searchTerm && !selectedCategory && (
        <div>
          {categories.map(category => (
            <div key={category} className="mb-4">
              <div
                className="flex items-center justify-between cursor-pointer mb-2"
                onClick={() => toggleCategory(category)}
              >
                <h3 className="text-md font-semibold text-gray-700">
                  {category}
                </h3>
                <i className={`fas fa-chevron-${expandedCategories[category] ? 'down' : 'right'} text-gray-500`}></i>
              </div>

              {expandedCategories[category] !== false && nodesByCategory[category] && (
                <div className="pl-2">
                  {nodesByCategory[category]
                    .filter(node => !showOnlyAvailable || node.status === 'available')
                    .map((node, index) => (
                      <NodeItem
                        key={`category-${category}-${node.id}-${index}`}
                        node={node}
                        isFavorite={favorites.includes(node.id)}
                        onToggleFavorite={toggleFavorite}
                        onNodeUsed={addToRecentlyUsed}
                      />
                    ))
                  }
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default NodeLibrary;
