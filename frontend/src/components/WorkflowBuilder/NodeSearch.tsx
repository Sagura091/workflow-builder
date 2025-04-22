import React, { useState, useEffect, useRef } from 'react';

import { NodeData } from '../../types';

// Extended NodeData type for search functionality
type SearchableNode = NodeData & {
  title?: string; // Make title explicitly optional
};

// Props interface for the NodeSearch component
interface NodeSearchProps {
  nodes: NodeData[];
  onSelectNode: (nodeId: string) => void;
  onClose: () => void;
}

const NodeSearch: React.FC<NodeSearchProps> = ({ nodes, onSelectNode, onClose }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredNodes, setFilteredNodes] = useState<SearchableNode[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  // Focus input on mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  // Filter nodes based on search term
  useEffect(() => {
    if (!searchTerm.trim()) {
      // Convert NodeData[] to SearchableNode[] to avoid type errors
      setFilteredNodes(nodes as SearchableNode[]);
      return;
    }

    const lowerSearchTerm = searchTerm.toLowerCase();
    const filtered = nodes.filter(node => {
      // Search in node type, title, and config
      const nodeType = node.type.toLowerCase();
      const nodeTitle = ((node as SearchableNode).title || '').toLowerCase();

      // Search in config values
      let configMatch = false;
      if (node.config) {
        configMatch = Object.values(node.config).some(value => {
          if (typeof value === 'string') {
            return value.toLowerCase().includes(lowerSearchTerm);
          } else if (typeof value === 'number' || typeof value === 'boolean') {
            return String(value).toLowerCase().includes(lowerSearchTerm);
          }
          return false;
        });
      }

      return nodeType.includes(lowerSearchTerm) ||
             nodeTitle.includes(lowerSearchTerm) ||
             configMatch;
    });

    setFilteredNodes(filtered);
    setSelectedIndex(0); // Reset selection when search changes
  }, [searchTerm, nodes]);

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => (prev + 1) % filteredNodes.length);
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => (prev - 1 + filteredNodes.length) % filteredNodes.length);
        break;
      case 'Enter':
        if (filteredNodes[selectedIndex]) {
          handleSelectNode(filteredNodes[selectedIndex].id);
        }
        break;
      case 'Escape':
        onClose();
        break;
    }
  };

  // Scroll selected item into view
  useEffect(() => {
    if (filteredNodes.length === 0) return;

    const selectedElement = document.getElementById(`search-result-${selectedIndex}`);
    if (selectedElement && resultsRef.current) {
      selectedElement.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }, [selectedIndex, filteredNodes.length]);

  const handleSelectNode = (nodeId: string) => {
    onSelectNode(nodeId);
    onClose();
  };

  // Get node type display name
  const getNodeTypeName = (type: string) => {
    // Remove namespace prefix (e.g., "core.text.text_input" -> "text_input")
    const parts = type.split('.');
    return parts[parts.length - 1].replace(/_/g, ' ');
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div
        className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col overflow-hidden"
        onKeyDown={handleKeyDown}
      >
        <div className="p-4 border-b border-gray-200 flex items-center">
          <i className="fas fa-search text-gray-400 mr-3"></i>
          <input
            ref={inputRef}
            type="text"
            className="flex-grow text-lg border-none outline-none"
            placeholder="Search nodes by type, title, or content..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button
            className="text-gray-400 hover:text-gray-600"
            onClick={onClose}
          >
            <i className="fas fa-times"></i>
          </button>
        </div>

        <div ref={resultsRef} className="overflow-y-auto flex-grow">
          {filteredNodes.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <i className="fas fa-search text-5xl mb-4 opacity-30"></i>
              <p>No nodes found matching "{searchTerm}"</p>
            </div>
          ) : (
            <ul className="divide-y divide-gray-100">
              {filteredNodes.map((node, index) => (
                <li
                  key={node.id}
                  id={`search-result-${index}`}
                  className={`p-3 hover:bg-blue-50 cursor-pointer transition-colors ${selectedIndex === index ? 'bg-blue-50' : ''}`}
                  onClick={() => handleSelectNode(node.id)}
                >
                  <div className="flex items-center">
                    <div
                      className="w-8 h-8 rounded-full flex items-center justify-center mr-3"
                      style={{ backgroundColor: getNodeColor(node.type) }}
                    >
                      <i className={`fas fa-${getNodeIcon(node.type)} text-white text-xs`}></i>
                    </div>
                    <div className="flex-grow">
                      <div className="font-medium">{(node as SearchableNode).title || getNodeTypeName(node.type)}</div>
                      <div className="text-xs text-gray-500 flex items-center">
                        <span className="mr-2">{node.type}</span>
                        <span className="text-gray-400">ID: {node.id.substring(0, 8)}</span>
                      </div>
                    </div>
                    <div className="text-xs text-gray-400">
                      {node.x.toFixed(0)}, {node.y.toFixed(0)}
                    </div>
                  </div>

                  {/* Show node config summary if available */}
                  {node.config && Object.keys(node.config).length > 0 && (
                    <div className="mt-2 ml-11 text-xs text-gray-600 bg-gray-50 p-2 rounded">
                      {Object.entries(node.config).map(([key, value]) => (
                        <div key={key} className="truncate">
                          <span className="font-medium">{key}:</span> {renderConfigValue(value)}
                        </div>
                      )).slice(0, 3)}
                      {Object.keys(node.config).length > 3 && (
                        <div className="text-gray-400 italic">+ {Object.keys(node.config).length - 3} more properties</div>
                      )}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="p-3 border-t border-gray-200 bg-gray-50 text-xs text-gray-500">
          <div className="flex justify-between">
            <div>
              <span className="mr-4"><kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs font-mono">↑</kbd> <kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs font-mono">↓</kbd> to navigate</span>
              <span className="mr-4"><kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs font-mono">Enter</kbd> to select</span>
              <span><kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs font-mono">Esc</kbd> to close</span>
            </div>
            <div>{filteredNodes.length} node{filteredNodes.length !== 1 ? 's' : ''} found</div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper functions for node visualization
const getNodeColor = (type: string): string => {
  const typeColors: Record<string, string> = {
    'core.begin': '#3b82f6', // blue
    'core.text': '#60a5fa', // light blue
    'core.variables': '#8b5cf6', // purple
    'core.control_flow': '#f97316', // orange
    'core.math': '#10b981', // green
    'core.file_storage': '#f59e0b', // amber
    'core.web_api': '#ec4899', // pink
    'core.converters': '#6366f1', // indigo
    'plugins': '#14b8a6', // teal
  };

  // Find the matching prefix
  for (const prefix in typeColors) {
    if (type.startsWith(prefix)) {
      return typeColors[prefix];
    }
  }

  return '#9ca3af'; // gray default
};

const getNodeIcon = (type: string): string => {
  const typeIcons: Record<string, string> = {
    'core.begin': 'play-circle',
    'core.text': 'font',
    'core.variables': 'database',
    'core.control_flow': 'code-branch',
    'core.math': 'calculator',
    'core.file_storage': 'file',
    'core.web_api': 'globe',
    'core.converters': 'exchange-alt',
    'plugins': 'puzzle-piece',
  };

  // Find the matching prefix
  for (const prefix in typeIcons) {
    if (type.startsWith(prefix)) {
      return typeIcons[prefix];
    }
  }

  return 'cube'; // default icon
};

const renderConfigValue = (value: unknown): string => {
  if (value === null || value === undefined) return 'null';
  if (typeof value === 'string') return value.length > 30 ? `"${value.substring(0, 30)}..."` : `"${value}"`;
  if (typeof value === 'object') return Array.isArray(value) ? `[Array(${value.length})]` : '{Object}';
  return String(value);
};

export default NodeSearch;
