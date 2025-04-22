import React, { useState, useRef, useEffect } from 'react';
import './FormControls.css';

interface ColorPickerProps {
  value: string;
  onChange: (value: string) => void;
  label?: string;
  helpText?: string;
}

const ColorPicker: React.FC<ColorPickerProps> = ({
  value,
  onChange,
  label,
  helpText
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentColor, setCurrentColor] = useState(value || '#3b82f6');
  const pickerRef = useRef<HTMLDivElement>(null);

  // Predefined color palette
  const colorPalette = [
    '#ef4444', '#f97316', '#f59e0b', '#eab308', 
    '#84cc16', '#22c55e', '#10b981', '#14b8a6',
    '#06b6d4', '#0ea5e9', '#3b82f6', '#6366f1',
    '#8b5cf6', '#a855f7', '#d946ef', '#ec4899',
    '#f43f5e', '#64748b', '#1e293b', '#000000'
  ];

  // Handle click outside to close the picker
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (pickerRef.current && !pickerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Update color and notify parent
  const handleColorChange = (color: string) => {
    setCurrentColor(color);
    onChange(color);
    setIsOpen(false);
  };

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newColor = e.target.value;
    setCurrentColor(newColor);
    onChange(newColor);
  };

  return (
    <div className="form-control-container">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      <div className="color-picker-container" ref={pickerRef}>
        <div className="color-picker-preview" onClick={() => setIsOpen(!isOpen)}>
          <div 
            className="color-swatch" 
            style={{ backgroundColor: currentColor }}
          ></div>
          <input
            type="text"
            value={currentColor}
            onChange={handleInputChange}
            className="color-input"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
        
        {isOpen && (
          <div className="color-picker-dropdown">
            <div className="color-palette">
              {colorPalette.map((color) => (
                <div
                  key={color}
                  className="color-option"
                  style={{ backgroundColor: color }}
                  onClick={() => handleColorChange(color)}
                ></div>
              ))}
            </div>
            <input
              type="color"
              value={currentColor}
              onChange={(e) => handleColorChange(e.target.value)}
              className="color-picker-input"
            />
          </div>
        )}
      </div>
      {helpText && (
        <p className="text-xs text-gray-500 mt-1">{helpText}</p>
      )}
    </div>
  );
};

export default ColorPicker;
