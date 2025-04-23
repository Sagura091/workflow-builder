# Version Management System

The Workflow Builder includes a version management system that allows both legacy and enhanced versions of components to coexist. This document explains how the system works and how to use it.

## Overview

The version management system provides the following features:

- **Dual Component Versions**: Both legacy and enhanced versions of components can be used simultaneously.
- **User Preferences**: Users can choose which version of a component to use.
- **Smooth Migration**: Gradual migration from legacy to enhanced components is supported.
- **Backward Compatibility**: Existing workflows continue to work with legacy components.

## Component Types

The version management system supports the following component types:

- **Core Nodes**: The built-in nodes provided by the workflow builder.
- **Plugins**: External components that extend the workflow builder.
- **Services**: Backend services that provide functionality to the workflow builder.
- **Controllers**: Backend controllers that handle API requests.
- **Models**: Data models used by the workflow builder.

## Version Preferences

For each component, you can set a preference for which version to use:

- **Legacy**: Use the original version of the component.
- **Enhanced**: Use the enhanced version of the component.

You can set preferences at two levels:

1. **Default Preference**: The default preference for all components of a type.
2. **Component Preference**: The preference for a specific component.

Component preferences override the default preference.

## API Endpoints

The version management system provides the following API endpoints:

### Get Version Information

```
GET /api/versions/
```

Returns version information for all components, including default preferences and mappings between legacy and enhanced versions.

### Get Core Node Versions

```
GET /api/versions/core-nodes
```

Returns version information for core nodes, including available versions and current preferences.

### Set Core Node Preference

```
POST /api/versions/core-nodes/{node_id}/preference
```

Sets the preference for a specific core node.

Parameters:
- `node_id`: The ID of the core node.
- `preference`: The preference to set ("legacy" or "enhanced").

### Set Default Core Node Preference

```
POST /api/versions/core-nodes/default-preference
```

Sets the default preference for all core nodes.

Parameters:
- `preference`: The preference to set ("legacy" or "enhanced").

### Get Plugin Versions

```
GET /api/versions/plugins
```

Returns version information for plugins, including available versions and current preferences.

### Set Plugin Preference

```
POST /api/versions/plugins/{plugin_id}/preference
```

Sets the preference for a specific plugin.

Parameters:
- `plugin_id`: The ID of the plugin.
- `preference`: The preference to set ("legacy" or "enhanced").

### Set Default Plugin Preference

```
POST /api/versions/plugins/default-preference
```

Sets the default preference for all plugins.

Parameters:
- `preference`: The preference to set ("legacy" or "enhanced").

## Environment Variables

The version management system uses the following environment variables:

- `USE_VERSIONED_CORE_NODES`: Whether to use the versioned core node registry. Default: `true`.
- `USE_ENHANCED_PLUGIN_MANAGER`: Whether to use the enhanced plugin manager. Default: `true`.

## Configuration File

The version management system stores its configuration in the following file:

```
backend/config/version_config.json
```

This file contains the following sections:

- `mappings`: Mappings between legacy and enhanced component IDs.
- `preferences`: User preferences for specific components.
- `default_preferences`: Default preferences for component types.

## Enhanced Core Nodes

The following core nodes have enhanced versions:

- `core.begin` -> `core.enhanced_begin`: Enhanced begin node with improved functionality.
- `core.end` -> `core.enhanced_end`: Enhanced end node with improved functionality.
- `core.conditional` -> `core.enhanced_conditional`: Enhanced conditional node with improved functionality.
- `core.loop` -> `core.enhanced_loop`: Enhanced loop node with improved functionality.
- `core.variable` -> `core.enhanced_variable`: Enhanced variable node with improved functionality.

## Enhanced Services

The following services have enhanced versions:

- `plugin_manager` -> `enhanced_plugin_manager`: Enhanced plugin manager with improved plugin discovery and lifecycle management.
- `core_node_registry` -> `enhanced_core_node_registry`: Enhanced core node registry with improved node discovery and categorization.

## Migration Guide

To migrate from legacy to enhanced components:

1. Set the default preference for a component type to "enhanced":

```
POST /api/versions/core-nodes/default-preference
{
  "preference": "enhanced"
}
```

2. Test your workflows to ensure they work correctly with enhanced components.

3. If you encounter issues with specific components, set their preference to "legacy":

```
POST /api/versions/core-nodes/{node_id}/preference
{
  "preference": "legacy"
}
```

4. Gradually migrate all components to enhanced versions as issues are resolved.

## Best Practices

- **Test Thoroughly**: Always test your workflows after changing version preferences.
- **Gradual Migration**: Migrate components gradually to minimize disruption.
- **Document Preferences**: Document which components use legacy versions and why.
- **Update Regularly**: Regularly check for updates to enhanced components.
- **Report Issues**: Report any issues with enhanced components to the development team.
