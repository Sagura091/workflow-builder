import React, { useState, useEffect } from 'react';
import CodeEditor from './CodeEditor';
import './FormControls.css';

interface JsonEditorProps {
  value: any;
  onChange: (value: any) => void;
  label?: string;
  height?: string;
  placeholder?: string;
  helpText?: string;
}

const JsonEditor: React.FC<JsonEditorProps> = ({
  value,
  onChange,
  label,
  height = '200px',
  placeholder = '{\n  "key": "value"\n}',
  helpText
}) => {
  // Convert value to JSON string for the editor
  const [jsonString, setJsonString] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  // Initialize the editor with the value
  useEffect(() => {
    try {
      const initialJson = typeof value === 'string' 
        ? value 
        : JSON.stringify(value, null, 2);
      setJsonString(initialJson);
      setError(null);
    } catch (e) {
      setJsonString('');
      setError('Invalid JSON value');
    }
  }, []);

  // Handle changes to the JSON string
  const handleJsonChange = (newJsonString: string) => {
    setJsonString(newJsonString);
    
    try {
      // Try to parse the JSON
      if (newJsonString.trim()) {
        const parsedJson = JSON.parse(newJsonString);
        onChange(parsedJson);
        setError(null);
      } else {
        onChange({});
        setError(null);
      }
    } catch (e) {
      // If parsing fails, keep the string but show an error
      setError('Invalid JSON: ' + (e as Error).message);
    }
  };

  return (
    <div className="form-control-container">
      <CodeEditor
        value={jsonString}
        onChange={handleJsonChange}
        language="json"
        height={height}
        placeholder={placeholder}
        label={label}
      />
      {error && (
        <p className="text-xs text-red-500 mt-1">{error}</p>
      )}
      {helpText && !error && (
        <p className="text-xs text-gray-500 mt-1">{helpText}</p>
      )}
    </div>
  );
};

export default JsonEditor;
