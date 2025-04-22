import React, { useState } from 'react';
import { useDrag } from 'react-dnd';
import { Plugin } from '../../types';

interface ComponentSidebarProps {
  plugins: Plugin[];
}

interface ComponentItemProps {
  type: string;
  title: string;
  description: string;
  icon: string;
  color: string;
}

const ComponentItem: React.FC<ComponentItemProps> = ({ type, title, description, icon, color }) => {
  const [{ isDragging }, drag] = useDrag({
    type: 'component',
    item: { type },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  });

  return (
    <div
      ref={drag}
      className={`component-item p-2 bg-gray-50 rounded border cursor-move ${isDragging ? 'dragging' : ''}`}
      data-type={type}
    >
      <div className="flex items-center">
        <i className={`fas fa-${icon} text-${color}-500 mr-2`}></i>
        <div>
          <div className="text-sm font-medium">{title}</div>
          <div className="text-xs text-gray-500">{description}</div>
        </div>
      </div>
    </div>
  );
};

const ComponentSidebar: React.FC<ComponentSidebarProps> = ({ plugins }) => {
  const [searchTerm, setSearchTerm] = useState('');

  // Function to get a color based on category
  const getPluginColor = (category: string): string => {
    const colorMap: Record<string, string> = {
      'Data': 'blue',
      'Processing': 'green',
      'Analysis': 'purple',
      'Visualization': 'indigo',
      'Machine Learning': 'red',
      'Deployment': 'amber',
      'Utilities': 'gray',
      'Plugins': 'teal'
    };

    return colorMap[category] || 'gray';
  };

  // Group components by category
  const groupedComponents: Record<string, ComponentItemProps[]> = {
    'Data Preparation': [
      { type: 'data_loader', title: 'Data Loader', description: 'Load dataset from source', icon: 'database', color: 'blue' },
      { type: 'data_transform', title: 'Data Transform', description: 'Apply transformations', icon: 'filter', color: 'green' },
      { type: 'feature_engineering', title: 'Feature Engineering', description: 'Create and select features', icon: 'cogs', color: 'purple' },
    ],
    'Models': [
      { type: 'train_model', title: 'Train Model', description: 'Train ML model', icon: 'brain', color: 'red' },
      { type: 'evaluate', title: 'Evaluate', description: 'Evaluate model performance', icon: 'chart-line', color: 'indigo' },
      { type: 'predict', title: 'Predict', description: 'Make predictions', icon: 'magic', color: 'amber' },
    ],
    'Deployment': [
      { type: 'deploy_model', title: 'Deploy Model', description: 'Deploy to production', icon: 'rocket', color: 'blue' },
      { type: 'monitoring', title: 'Monitoring', description: 'Monitor model metrics', icon: 'heartbeat', color: 'red' },
    ],
  };

  // Add plugins from backend
  if (plugins && plugins.length > 0) {
    // Group plugins by category
    const pluginsByCategory: Record<string, ComponentItemProps[]> = {};

    plugins
      .filter(plugin => plugin && plugin.__plugin_meta__) // Filter out undefined plugins
      .forEach(plugin => {
        const meta = plugin.__plugin_meta__;
        const category = meta?.category || 'Plugins';

        if (!pluginsByCategory[category]) {
          pluginsByCategory[category] = [];
        }

        pluginsByCategory[category].push({
          type: plugin.id,
          title: meta?.name || 'Unknown Plugin',
          description: meta?.description || 'No description available',
          icon: 'puzzle-piece', // Default icon for plugins
          color: getPluginColor(category)
        });
      });

    // Add each category to grouped components
    Object.entries(pluginsByCategory).forEach(([category, items]) => {
      groupedComponents[`${category} (${items.length})`] = items;
    });
  }

  // Filter components based on search term
  const filterComponents = (components: ComponentItemProps[]) => {
    if (!searchTerm) return components;

    return components.filter(component =>
      component.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      component.description.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  // Count total plugins
  const pluginCount = Object.entries(groupedComponents)
    .filter(([category]) => category.includes('Plugins') || category.includes('Data') || category.includes('Processing'))
    .reduce((count, [_, components]) => count + components.length, 0);

  return (
    <div className="col-span-3">
      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-700">Workflow Components</h2>
          {pluginCount > 0 && (
            <span className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
              {pluginCount} Plugins Available
            </span>
          )}
        </div>

        {/* Search components */}
        <div className="mb-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <i className="fas fa-search text-gray-400"></i>
            </div>
            <input
              type="text"
              id="component-search"
              placeholder="Search components..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full border rounded-lg pl-10 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Component categories */}
        {Object.entries(groupedComponents).map(([category, components]) => {
          const filteredComponents = filterComponents(components);
          if (filteredComponents.length === 0) return null;

          // Check if this is a plugin category
          const isPluginCategory = category.includes('Plugins') || category.includes('Data') || category.includes('Processing');

          return (
            <div className={`mb-4 ${isPluginCategory ? 'relative' : ''}`} key={category}>
              <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                {category}
                {isPluginCategory && (
                  <span className="ml-2 bg-blue-100 text-blue-800 text-xs font-medium px-2 py-0.5 rounded">
                    New
                  </span>
                )}
              </h3>
              <div className="space-y-2">
                {filteredComponents.map((component) => (
                  <ComponentItem
                    key={component.type}
                    type={component.type}
                    title={component.title}
                    description={component.description}
                    icon={component.icon}
                    color={component.color}
                  />
                ))}
              </div>
              {isPluginCategory && (
                <div className="absolute -left-1 top-0 bottom-0 w-1 bg-blue-500 rounded"></div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ComponentSidebar;
