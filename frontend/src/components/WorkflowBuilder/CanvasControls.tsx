import React from 'react';

interface CanvasControlsProps {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onZoomReset: () => void;
  onCenterView: () => void;
  onSearch: () => void;
  onUndo: () => void;
  onRedo: () => void;
  zoomLevel: number;
}

const CanvasControls: React.FC<CanvasControlsProps> = ({
  onZoomIn,
  onZoomOut,
  onZoomReset,
  onCenterView,
  onSearch,
  onUndo,
  onRedo,
  zoomLevel
}) => {
  return (
    <div className="canvas-controls">
      <button
        onClick={onZoomIn}
        className="p-1 hover:bg-gray-100 rounded"
        title="Zoom In"
      >
        <i className="fas fa-search-plus"></i>
      </button>
      <button
        onClick={onZoomOut}
        className="p-1 hover:bg-gray-100 rounded"
        title="Zoom Out"
      >
        <i className="fas fa-search-minus"></i>
      </button>
      <button
        onClick={onZoomReset}
        className="p-1 hover:bg-gray-100 rounded"
        title="Reset Zoom"
      >
        <i className="fas fa-compress-arrows-alt"></i>
      </button>
      <button
        onClick={onCenterView}
        className="p-1 hover:bg-gray-100 rounded"
        title="Center View (C)"
      >
        <i className="fas fa-bullseye"></i>
      </button>

      <div className="border-r border-gray-300 mx-1 h-6"></div>

      <button
        onClick={onUndo}
        className="p-1 hover:bg-gray-100 rounded"
        title="Undo"
      >
        <i className="fas fa-undo"></i>
      </button>
      <button
        onClick={onRedo}
        className="p-1 hover:bg-gray-100 rounded"
        title="Redo"
      >
        <i className="fas fa-redo"></i>
      </button>

      <div className="border-r border-gray-300 mx-1 h-6"></div>

      <button
        onClick={onSearch}
        className="p-1 hover:bg-gray-100 rounded"
        title="Search Nodes (Ctrl+F)"
      >
        <i className="fas fa-search"></i>
      </button>

      <button
        className="p-1 hover:bg-gray-100 rounded"
        title="Validate Workflow"
      >
        <i className="fas fa-check-circle"></i>
      </button>

      {/* Zoom level indicator */}
      <div className="ml-2 text-xs text-gray-500 flex items-center">
        {Math.round(zoomLevel * 100)}%
      </div>
    </div>
  );
};

export default CanvasControls;
