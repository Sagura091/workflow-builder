import React, { useState } from 'react';
import './FormControls.css';

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: 'javascript' | 'python' | 'json' | 'html' | 'css';
  height?: string;
  placeholder?: string;
  label?: string;
  helpText?: string;
}

const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  onChange,
  language = 'javascript',
  height = '200px',
  placeholder = 'Enter code here...',
  label,
  helpText
}) => {
  const [isFocused, setIsFocused] = useState(false);

  // Get syntax highlighting class based on language
  const getSyntaxClass = () => {
    switch (language) {
      case 'javascript':
        return 'language-javascript';
      case 'python':
        return 'language-python';
      case 'json':
        return 'language-json';
      case 'html':
        return 'language-html';
      case 'css':
        return 'language-css';
      default:
        return 'language-javascript';
    }
  };

  // Format code on blur
  const handleBlur = () => {
    setIsFocused(false);
    
    // Basic formatting for JSON
    if (language === 'json' && value.trim()) {
      try {
        const formatted = JSON.stringify(JSON.parse(value), null, 2);
        onChange(formatted);
      } catch (e) {
        // If not valid JSON, leave as is
        console.warn('Invalid JSON, skipping formatting');
      }
    }
  };

  return (
    <div className="form-control-container">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      <div 
        className={`code-editor-container ${isFocused ? 'focused' : ''} ${getSyntaxClass()}`}
        style={{ height }}
      >
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={handleBlur}
          placeholder={placeholder}
          className="code-editor-textarea"
          spellCheck={false}
        />
        <pre className="code-editor-highlight">
          <code className={getSyntaxClass()}>
            {value || placeholder}
          </code>
        </pre>
      </div>
      {helpText && (
        <p className="text-xs text-gray-500 mt-1">{helpText}</p>
      )}
    </div>
  );
};

export default CodeEditor;
