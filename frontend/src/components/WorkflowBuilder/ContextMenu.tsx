import React, { useEffect, useRef } from 'react';

interface ContextMenuProps {
  x: number;
  y: number;
  onClose: () => void;
  onAddNode: (type: string, x: number, y: number) => string;
  onPaste: () => void;
  onSelectAll: () => void;
  onClearCanvas: () => void;
  onShowShortcuts: () => void;
  onCenterView: () => void;
  onSearch: () => void;
}

const ContextMenu: React.FC<ContextMenuProps> = ({
  x,
  y,
  onClose,
  onAddNode,
  onPaste,
  onSelectAll,
  onClearCanvas,
  onShowShortcuts,
  onCenterView,
  onSearch
}) => {
  const menuRef = useRef<HTMLDivElement>(null);

  // Close the menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [onClose]);

  // Common node types for quick access
  const commonNodeTypes = [
    { type: 'core.begin', label: 'Begin', icon: 'play-circle' },
    { type: 'core.text.text_input', label: 'Text Input', icon: 'font' },
    { type: 'core.variables.set_variable', label: 'Set Variable', icon: 'database' },
    { type: 'core.control_flow.if_condition', label: 'If Condition', icon: 'code-branch' },
    { type: 'core.control_flow.for_loop', label: 'For Loop', icon: 'redo' }
  ];

  return (
    <div
      ref={menuRef}
      className="absolute bg-white rounded-lg shadow-xl border border-gray-200 z-50 w-64 overflow-hidden"
      style={{
        left: `${x}px`,
        top: `${y}px`,
        maxHeight: '80vh',
        transform: 'translate(-50%, -50%)'
      }}
    >
      <div className="p-2 bg-gray-50 border-b border-gray-200">
        <h3 className="text-sm font-medium text-gray-700">Quick Actions</h3>
      </div>

      <div className="p-2">
        <div className="mb-3">
          <div className="text-xs font-medium text-gray-500 mb-1 uppercase tracking-wider">Common Nodes</div>
          <div className="grid grid-cols-3 gap-1">
            {commonNodeTypes.map((node) => (
              <button
                key={node.type}
                className="flex flex-col items-center justify-center p-2 rounded hover:bg-blue-50 transition-colors text-gray-700 hover:text-blue-700"
                onClick={() => {
                  onAddNode(node.type, x, y);
                  onClose();
                }}
              >
                <i className={`fas fa-${node.icon} text-lg mb-1`}></i>
                <span className="text-xs">{node.label}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="border-t border-gray-100 pt-2">
          <button
            className="w-full text-left px-3 py-2 hover:bg-blue-50 text-sm flex items-center text-gray-700 hover:text-blue-700"
            onClick={() => {
              onPaste();
              onClose();
            }}
          >
            <i className="fas fa-paste w-5 text-center mr-2"></i> Paste
            <span className="ml-auto text-xs text-gray-400">Ctrl+V</span>
          </button>

          <button
            className="w-full text-left px-3 py-2 hover:bg-blue-50 text-sm flex items-center text-gray-700 hover:text-blue-700"
            onClick={() => {
              onSelectAll();
              onClose();
            }}
          >
            <i className="fas fa-object-group w-5 text-center mr-2"></i> Select All
            <span className="ml-auto text-xs text-gray-400">Ctrl+A</span>
          </button>

          <button
            className="w-full text-left px-3 py-2 hover:bg-blue-50 text-sm flex items-center text-gray-700 hover:text-blue-700"
            onClick={() => {
              onClearCanvas();
              onClose();
            }}
          >
            <i className="fas fa-trash-alt w-5 text-center mr-2"></i> Clear Canvas
          </button>

          <button
            className="w-full text-left px-3 py-2 hover:bg-blue-50 text-sm flex items-center text-gray-700 hover:text-blue-700"
            onClick={() => {
              onCenterView();
              onClose();
            }}
          >
            <i className="fas fa-bullseye w-5 text-center mr-2"></i> Center View
            <span className="ml-auto text-xs text-gray-400">C</span>
          </button>

          <button
            className="w-full text-left px-3 py-2 hover:bg-blue-50 text-sm flex items-center text-gray-700 hover:text-blue-700"
            onClick={() => {
              onSearch();
              onClose();
            }}
          >
            <i className="fas fa-search w-5 text-center mr-2"></i> Search Nodes
            <span className="ml-auto text-xs text-gray-400">Ctrl+F</span>
          </button>

          <button
            className="w-full text-left px-3 py-2 hover:bg-blue-50 text-sm flex items-center text-gray-700 hover:text-blue-700"
            onClick={() => {
              onShowShortcuts();
              onClose();
            }}
          >
            <i className="fas fa-keyboard w-5 text-center mr-2"></i> Keyboard Shortcuts
            <span className="ml-auto text-xs text-gray-400">?</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ContextMenu;
