import React, { useRef, useEffect, useState } from 'react';
import { NodeData } from '../../types';

interface MinimapProps {
  nodes: NodeData[];
  canvasSize: { width: number; height: number };
  zoomLevel: number;
  panOffset: { x: number; y: number };
  onPanChange: (offset: { x: number; y: number }) => void;
}

const Minimap: React.FC<MinimapProps> = ({
  nodes,
  canvasSize,
  zoomLevel,
  panOffset,
  onPanChange
}) => {
  const minimapRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [scale, setScale] = useState(0.1);
  const [bounds, setBounds] = useState({ minX: 0, minY: 0, maxX: 0, maxY: 0 });

  // Calculate bounds of all nodes
  useEffect(() => {
    if (nodes.length === 0) {
      setBounds({ minX: 0, minY: 0, maxX: 0, maxY: 0 });
      return;
    }

    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;

    nodes.forEach(node => {
      minX = Math.min(minX, node.x);
      minY = Math.min(minY, node.y);
      maxX = Math.max(maxX, node.x + (node.width || 240)); // Assuming default width
      maxY = Math.max(maxY, node.y + (node.height || 100)); // Assuming default height
    });

    // Add some padding
    minX -= 100;
    minY -= 100;
    maxX += 100;
    maxY += 100;

    setBounds({ minX, minY, maxX, maxY });

    // Calculate scale based on minimap size and content bounds
    if (minimapRef.current) {
      const minimapWidth = minimapRef.current.clientWidth;
      const minimapHeight = minimapRef.current.clientHeight;
      const contentWidth = maxX - minX;
      const contentHeight = maxY - minY;
      
      const scaleX = minimapWidth / contentWidth;
      const scaleY = minimapHeight / contentHeight;
      setScale(Math.min(scaleX, scaleY, 0.1)); // Cap at 0.1 to prevent too large scaling
    }
  }, [nodes]);

  // Handle minimap click/drag
  const handleMinimapMouseDown = (e: React.MouseEvent) => {
    if (!minimapRef.current) return;
    
    setIsDragging(true);
    const rect = minimapRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Calculate new pan offset
    updatePanOffset(x, y);
  };

  const handleMinimapMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !minimapRef.current) return;
    
    const rect = minimapRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Calculate new pan offset
    updatePanOffset(x, y);
  };

  const handleMinimapMouseUp = () => {
    setIsDragging(false);
  };

  const updatePanOffset = (x: number, y: number) => {
    if (!minimapRef.current) return;
    
    const minimapWidth = minimapRef.current.clientWidth;
    const minimapHeight = minimapRef.current.clientHeight;
    
    // Convert minimap coordinates to canvas coordinates
    const canvasX = (x / scale) + bounds.minX;
    const canvasY = (y / scale) + bounds.minY;
    
    // Calculate new pan offset
    const newPanX = -(canvasX * zoomLevel) + (canvasSize.width / 2);
    const newPanY = -(canvasY * zoomLevel) + (canvasSize.height / 2);
    
    onPanChange({ x: newPanX, y: newPanY });
  };

  // Calculate viewport rectangle
  const getViewportRect = () => {
    if (!minimapRef.current) return { left: 0, top: 0, width: 0, height: 0 };
    
    const minimapWidth = minimapRef.current.clientWidth;
    const minimapHeight = minimapRef.current.clientHeight;
    
    // Calculate visible area in canvas coordinates
    const visibleLeft = -panOffset.x / zoomLevel;
    const visibleTop = -panOffset.y / zoomLevel;
    const visibleWidth = canvasSize.width / zoomLevel;
    const visibleHeight = canvasSize.height / zoomLevel;
    
    // Convert to minimap coordinates
    const rectLeft = (visibleLeft - bounds.minX) * scale;
    const rectTop = (visibleTop - bounds.minY) * scale;
    const rectWidth = visibleWidth * scale;
    const rectHeight = visibleHeight * scale;
    
    return {
      left: Math.max(0, Math.min(minimapWidth - rectWidth, rectLeft)),
      top: Math.max(0, Math.min(minimapHeight - rectHeight, rectTop)),
      width: Math.min(minimapWidth, rectWidth),
      height: Math.min(minimapHeight, rectHeight)
    };
  };

  const viewport = getViewportRect();

  return (
    <div 
      ref={minimapRef}
      className="workflow-minimap"
      onMouseDown={handleMinimapMouseDown}
      onMouseMove={handleMinimapMouseMove}
      onMouseUp={handleMinimapMouseUp}
      onMouseLeave={handleMinimapMouseUp}
    >
      {/* Minimap content */}
      <div className="relative w-full h-full">
        {/* Node representations */}
        {nodes.map(node => {
          const left = (node.x - bounds.minX) * scale;
          const top = (node.y - bounds.minY) * scale;
          const width = ((node.width || 240) * scale);
          const height = ((node.height || 100) * scale);
          
          return (
            <div
              key={node.id}
              className="absolute bg-gray-400"
              style={{
                left: `${left}px`,
                top: `${top}px`,
                width: `${width}px`,
                height: `${height}px`,
                borderRadius: '2px'
              }}
            />
          );
        })}
        
        {/* Viewport rectangle */}
        <div
          className="absolute border-2 border-blue-500 bg-blue-100 bg-opacity-30"
          style={{
            left: `${viewport.left}px`,
            top: `${viewport.top}px`,
            width: `${viewport.width}px`,
            height: `${viewport.height}px`
          }}
        />
      </div>
    </div>
  );
};

export default Minimap;
