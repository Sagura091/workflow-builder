import { useEffect, useCallback } from 'react';

// Shortcut categories
export enum ShortcutCategory {
  GENERAL = 'General',
  CANVAS = 'Canvas',
  NODES = 'Nodes',
  CONNECTIONS = 'Connections',
  EXECUTION = 'Execution',
  PANELS = 'Panels',
}

// Shortcut interface
export interface Shortcut {
  id: string;
  key: string;
  description: string;
  category: ShortcutCategory;
  ctrlKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  metaKey?: boolean;
  action: () => void;
}

// Format key combination for display
export const formatKeyCombination = (shortcut: Shortcut): string => {
  const parts: string[] = [];

  if (shortcut.ctrlKey) parts.push('Ctrl');
  if (shortcut.shiftKey) parts.push('Shift');
  if (shortcut.altKey) parts.push('Alt');
  if (shortcut.metaKey) parts.push('⌘');

  // Format the key
  let key = shortcut.key;
  if (key === ' ') key = 'Space';
  if (key === 'ArrowUp') key = '↑';
  if (key === 'ArrowDown') key = '↓';
  if (key === 'ArrowLeft') key = '←';
  if (key === 'ArrowRight') key = '→';
  if (key === 'Delete') key = 'Del';
  if (key === 'Escape') key = 'Esc';

  parts.push(key.toUpperCase());

  return parts.join(' + ');
};

// Check if a keyboard event matches a shortcut
export const matchesShortcut = (event: KeyboardEvent, shortcut: Shortcut): boolean => {
  return (
    event.key.toLowerCase() === shortcut.key.toLowerCase() &&
    !!event.ctrlKey === !!shortcut.ctrlKey &&
    !!event.shiftKey === !!shortcut.shiftKey &&
    !!event.altKey === !!shortcut.altKey &&
    !!event.metaKey === !!shortcut.metaKey
  );
};

// Hook to register keyboard shortcuts
export const useKeyboardShortcuts = (shortcuts: Shortcut[]) => {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Skip if the event target is an input, textarea, or select
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement ||
        event.target instanceof HTMLSelectElement
      ) {
        return;
      }

      for (const shortcut of shortcuts) {
        if (matchesShortcut(event, shortcut)) {
          event.preventDefault();
          shortcut.action();
          break;
        }
      }
    },
    [shortcuts]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);
};

// Default shortcuts
export const getDefaultShortcuts = (actions: Record<string, () => void>): Shortcut[] => [
  // General shortcuts
  {
    id: 'new-workflow',
    key: 'n',
    ctrlKey: true,
    description: 'Create a new workflow',
    category: ShortcutCategory.GENERAL,
    action: actions.newWorkflow || (() => {}),
  },
  {
    id: 'save-workflow',
    key: 's',
    ctrlKey: true,
    description: 'Save workflow',
    category: ShortcutCategory.GENERAL,
    action: actions.saveWorkflow || (() => {}),
  },
  {
    id: 'open-workflow',
    key: 'o',
    ctrlKey: true,
    description: 'Open workflow',
    category: ShortcutCategory.GENERAL,
    action: actions.openWorkflow || (() => {}),
  },
  {
    id: 'undo',
    key: 'z',
    ctrlKey: true,
    description: 'Undo',
    category: ShortcutCategory.GENERAL,
    action: actions.undo || (() => {}),
  },
  {
    id: 'redo',
    key: 'y',
    ctrlKey: true,
    description: 'Redo',
    category: ShortcutCategory.GENERAL,
    action: actions.redo || (() => {}),
  },
  {
    id: 'help',
    key: '?',
    description: 'Show keyboard shortcuts',
    category: ShortcutCategory.GENERAL,
    action: actions.showShortcuts || (() => {}),
  },

  // Canvas shortcuts
  {
    id: 'zoom-in',
    key: '=',
    ctrlKey: true,
    description: 'Zoom in',
    category: ShortcutCategory.CANVAS,
    action: actions.zoomIn || (() => {}),
  },
  {
    id: 'zoom-out',
    key: '-',
    ctrlKey: true,
    description: 'Zoom out',
    category: ShortcutCategory.CANVAS,
    action: actions.zoomOut || (() => {}),
  },
  {
    id: 'zoom-reset',
    key: '0',
    ctrlKey: true,
    description: 'Reset zoom',
    category: ShortcutCategory.CANVAS,
    action: actions.zoomReset || (() => {}),
  },
  {
    id: 'pan-up',
    key: 'ArrowUp',
    description: 'Pan up',
    category: ShortcutCategory.CANVAS,
    action: actions.panUp || (() => {}),
  },
  {
    id: 'pan-down',
    key: 'ArrowDown',
    description: 'Pan down',
    category: ShortcutCategory.CANVAS,
    action: actions.panDown || (() => {}),
  },
  {
    id: 'pan-left',
    key: 'ArrowLeft',
    description: 'Pan left',
    category: ShortcutCategory.CANVAS,
    action: actions.panLeft || (() => {}),
  },
  {
    id: 'pan-right',
    key: 'ArrowRight',
    description: 'Pan right',
    category: ShortcutCategory.CANVAS,
    action: actions.panRight || (() => {}),
  },

  // Node shortcuts
  {
    id: 'delete-selected',
    key: 'Delete',
    description: 'Delete selected node or connection',
    category: ShortcutCategory.NODES,
    action: actions.deleteSelected || (() => {}),
  },
  {
    id: 'duplicate-node',
    key: 'd',
    ctrlKey: true,
    description: 'Duplicate selected node',
    category: ShortcutCategory.NODES,
    action: actions.duplicateNode || (() => {}),
  },
  {
    id: 'select-all-nodes',
    key: 'a',
    ctrlKey: true,
    description: 'Select all nodes',
    category: ShortcutCategory.NODES,
    action: actions.selectAllNodes || (() => {}),
  },
  {
    id: 'deselect-all',
    key: 'Escape',
    description: 'Deselect all',
    category: ShortcutCategory.NODES,
    action: actions.deselectAll || (() => {}),
  },
  {
    id: 'edit-node',
    key: 'e',
    description: 'Edit selected node',
    category: ShortcutCategory.NODES,
    action: actions.editNode || (() => {}),
  },

  // Execution shortcuts
  {
    id: 'execute-workflow',
    key: 'F5',
    description: 'Execute workflow',
    category: ShortcutCategory.EXECUTION,
    action: actions.executeWorkflow || (() => {}),
  },
  {
    id: 'stop-execution',
    key: 'F6',
    description: 'Stop execution',
    category: ShortcutCategory.EXECUTION,
    action: actions.stopExecution || (() => {}),
  },

  // Panel shortcuts
  {
    id: 'toggle-node-library',
    key: '1',
    altKey: true,
    description: 'Toggle Node Library panel',
    category: ShortcutCategory.PANELS,
    action: actions.toggleNodeLibrary || (() => {}),
  },
  {
    id: 'toggle-properties-panel',
    key: '2',
    altKey: true,
    description: 'Toggle Properties panel',
    category: ShortcutCategory.PANELS,
    action: actions.togglePropertiesPanel || (() => {}),
  },
  {
    id: 'toggle-all-panels',
    key: '`',
    description: 'Toggle all panels',
    category: ShortcutCategory.PANELS,
    action: actions.toggleAllPanels || (() => {}),
  },
  {
    id: 'maximize-canvas',
    key: 'F11',
    description: 'Maximize canvas (hide all panels)',
    category: ShortcutCategory.PANELS,
    action: actions.maximizeCanvas || (() => {}),
  },
  {
    id: 'restore-panels',
    key: 'Escape',
    altKey: true,
    description: 'Restore all panels',
    category: ShortcutCategory.PANELS,
    action: actions.restorePanels || (() => {}),
  }
];
