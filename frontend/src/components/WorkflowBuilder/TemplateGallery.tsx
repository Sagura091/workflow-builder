import React, { useState } from 'react';
import {
  templates,
  WorkflowTemplate,
  TemplateCategory
} from '../../templates';
import { Workflow } from '../../types';
import './TemplateGallery.css';

interface TemplateGalleryProps {
  onSelectTemplate: (workflow: Workflow) => void;
  onClose: () => void;
}

const TemplateGallery: React.FC<TemplateGalleryProps> = ({
  onSelectTemplate,
  onClose
}) => {
  const [selectedCategory, setSelectedCategory] = useState<TemplateCategory | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<WorkflowTemplate | null>(null);

  // Filter templates based on category and search query
  const filteredTemplates = templates.filter((template: WorkflowTemplate) => {
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    const matchesSearch =
      template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.tags.some((tag: string) => tag.toLowerCase().includes(searchQuery.toLowerCase()));

    return matchesCategory && matchesSearch;
  });

  // Group templates by category
  const templatesByCategory = filteredTemplates.reduce((acc, template) => {
    if (!acc[template.category]) {
      acc[template.category] = [];
    }
    acc[template.category].push(template);
    return acc;
  }, {} as Record<TemplateCategory, WorkflowTemplate[]>);

  // Handle template selection
  const handleSelectTemplate = (template: WorkflowTemplate) => {
    setSelectedTemplate(template);
  };

  // Handle template use
  const handleUseTemplate = () => {
    if (selectedTemplate) {
      onSelectTemplate({
        ...selectedTemplate.workflow,
        id: null, // Ensure we're creating a new workflow
        name: `${selectedTemplate.name} Copy`,
      });
      onClose();
    }
  };

  // Get difficulty badge color
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'intermediate':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
      case 'advanced':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  return (
    <div className="template-gallery-overlay">
      <div className="template-gallery-container bg-white dark:bg-dark-800 shadow-xl rounded-lg">
        <div className="template-gallery-header flex justify-between items-center p-4 border-b border-gray-200 dark:border-dark-600">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Workflow Templates</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="template-gallery-content flex h-[calc(100%-8rem)]">
          {/* Sidebar */}
          <div className="template-gallery-sidebar w-64 border-r border-gray-200 dark:border-dark-600 p-4 overflow-y-auto">
            <div className="mb-4">
              <input
                type="text"
                placeholder="Search templates..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-dark-600 rounded-md bg-white dark:bg-dark-700 text-gray-900 dark:text-gray-100"
              />
            </div>

            <div className="mb-4">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                Categories
              </h3>
              <ul>
                <li className="mb-1">
                  <button
                    className={`w-full text-left px-2 py-1 rounded-md ${
                      selectedCategory === 'all'
                        ? 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200'
                        : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-dark-700'
                    }`}
                    onClick={() => setSelectedCategory('all')}
                  >
                    All Templates
                  </button>
                </li>
                {Object.values(TemplateCategory).map((category) => (
                  <li key={category} className="mb-1">
                    <button
                      className={`w-full text-left px-2 py-1 rounded-md ${
                        selectedCategory === category
                          ? 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200'
                          : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-dark-700'
                      }`}
                      onClick={() => setSelectedCategory(category)}
                    >
                      {category}
                    </button>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                Difficulty
              </h3>
              <div className="flex flex-wrap gap-2">
                <span className={`px-2 py-1 rounded-md text-xs ${getDifficultyColor('beginner')}`}>
                  Beginner
                </span>
                <span className={`px-2 py-1 rounded-md text-xs ${getDifficultyColor('intermediate')}`}>
                  Intermediate
                </span>
                <span className={`px-2 py-1 rounded-md text-xs ${getDifficultyColor('advanced')}`}>
                  Advanced
                </span>
              </div>
            </div>
          </div>

          {/* Template list */}
          <div className="template-gallery-templates flex-1 p-4 overflow-y-auto">
            {filteredTemplates.length === 0 ? (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                No templates found matching your criteria.
              </div>
            ) : (
              <>
                {selectedCategory === 'all' ? (
                  // Group by category when "All" is selected
                  Object.entries(templatesByCategory).map(([category, categoryTemplates]) => (
                    <div key={category} className="mb-8">
                      <h3 className="text-lg font-medium text-gray-800 dark:text-white mb-4">
                        {category}
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {categoryTemplates.map((template) => (
                          <div
                            key={template.id}
                            className={`template-card border rounded-lg overflow-hidden cursor-pointer transition-all duration-200 ${
                              selectedTemplate?.id === template.id
                                ? 'border-indigo-500 ring-2 ring-indigo-500 dark:border-indigo-400 dark:ring-indigo-400'
                                : 'border-gray-200 hover:border-indigo-300 dark:border-dark-600 dark:hover:border-indigo-700'
                            }`}
                            onClick={() => handleSelectTemplate(template)}
                          >
                            <div className="template-card-preview h-32 bg-gray-100 dark:bg-dark-700 flex items-center justify-center">
                              {template.thumbnail ? (
                                <img
                                  src={template.thumbnail}
                                  alt={template.name}
                                  className="max-h-full max-w-full object-contain"
                                />
                              ) : (
                                <div className="text-gray-400 dark:text-gray-600">
                                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path
                                      strokeLinecap="round"
                                      strokeLinejoin="round"
                                      strokeWidth="2"
                                      d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"
                                    />
                                  </svg>
                                </div>
                              )}
                            </div>
                            <div className="p-4">
                              <h4 className="font-medium text-gray-900 dark:text-white mb-1">{template.name}</h4>
                              <p className="text-sm text-gray-500 dark:text-gray-400 mb-2 line-clamp-2">
                                {template.description}
                              </p>
                              <div className="flex flex-wrap gap-1 mt-2">
                                <span className={`px-2 py-0.5 rounded-md text-xs ${getDifficultyColor(template.difficulty)}`}>
                                  {template.difficulty.charAt(0).toUpperCase() + template.difficulty.slice(1)}
                                </span>
                                {template.tags.slice(0, 2).map((tag) => (
                                  <span
                                    key={tag}
                                    className="px-2 py-0.5 rounded-md text-xs bg-gray-100 text-gray-600 dark:bg-dark-700 dark:text-gray-300"
                                  >
                                    {tag}
                                  </span>
                                ))}
                                {template.tags.length > 2 && (
                                  <span className="px-2 py-0.5 rounded-md text-xs bg-gray-100 text-gray-600 dark:bg-dark-700 dark:text-gray-300">
                                    +{template.tags.length - 2}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))
                ) : (
                  // Show flat list when a specific category is selected
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredTemplates.map((template) => (
                      <div
                        key={template.id}
                        className={`template-card border rounded-lg overflow-hidden cursor-pointer transition-all duration-200 ${
                          selectedTemplate?.id === template.id
                            ? 'border-indigo-500 ring-2 ring-indigo-500 dark:border-indigo-400 dark:ring-indigo-400'
                            : 'border-gray-200 hover:border-indigo-300 dark:border-dark-600 dark:hover:border-indigo-700'
                        }`}
                        onClick={() => handleSelectTemplate(template)}
                      >
                        <div className="template-card-preview h-32 bg-gray-100 dark:bg-dark-700 flex items-center justify-center">
                          {template.thumbnail ? (
                            <img
                              src={template.thumbnail}
                              alt={template.name}
                              className="max-h-full max-w-full object-contain"
                            />
                          ) : (
                            <div className="text-gray-400 dark:text-gray-600">
                              <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth="2"
                                  d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"
                                />
                              </svg>
                            </div>
                          )}
                        </div>
                        <div className="p-4">
                          <h4 className="font-medium text-gray-900 dark:text-white mb-1">{template.name}</h4>
                          <p className="text-sm text-gray-500 dark:text-gray-400 mb-2 line-clamp-2">
                            {template.description}
                          </p>
                          <div className="flex flex-wrap gap-1 mt-2">
                            <span className={`px-2 py-0.5 rounded-md text-xs ${getDifficultyColor(template.difficulty)}`}>
                              {template.difficulty.charAt(0).toUpperCase() + template.difficulty.slice(1)}
                            </span>
                            {template.tags.slice(0, 2).map((tag) => (
                              <span
                                key={tag}
                                className="px-2 py-0.5 rounded-md text-xs bg-gray-100 text-gray-600 dark:bg-dark-700 dark:text-gray-300"
                              >
                                {tag}
                              </span>
                            ))}
                            {template.tags.length > 2 && (
                              <span className="px-2 py-0.5 rounded-md text-xs bg-gray-100 text-gray-600 dark:bg-dark-700 dark:text-gray-300">
                                +{template.tags.length - 2}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="template-gallery-footer p-4 border-t border-gray-200 dark:border-dark-600 flex justify-between items-center">
          <div>
            {selectedTemplate && (
              <div className="text-sm text-gray-500 dark:text-gray-400">
                Selected: <span className="font-medium text-gray-700 dark:text-gray-300">{selectedTemplate.name}</span>
              </div>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 dark:border-dark-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-dark-700"
            >
              Cancel
            </button>
            <button
              onClick={handleUseTemplate}
              disabled={!selectedTemplate}
              className={`px-4 py-2 rounded-md ${
                selectedTemplate
                  ? 'bg-indigo-600 text-white hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-800'
                  : 'bg-indigo-300 text-white cursor-not-allowed dark:bg-indigo-900'
              }`}
            >
              Use Template
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemplateGallery;
