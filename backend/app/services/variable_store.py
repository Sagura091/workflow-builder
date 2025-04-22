"""
Variable Store

This module provides a store for workflow variables.
"""

class VariableStore:
    """
    Store for workflow variables.
    
    This class provides a simple key-value store for variables used in workflows.
    Variables can be of any type and are accessed by name.
    """
    
    def __init__(self):
        """Initialize an empty variable store."""
        self.variables = {}
    
    def get(self, name, default=None):
        """
        Get a variable value.
        
        Args:
            name (str): The name of the variable
            default: The default value to return if the variable doesn't exist
            
        Returns:
            The variable value, or the default if the variable doesn't exist
        """
        return self.variables.get(name, default)
    
    def set(self, name, value):
        """
        Set a variable value.
        
        Args:
            name (str): The name of the variable
            value: The value to set
            
        Returns:
            The value that was set
        """
        self.variables[name] = value
        return value
    
    def delete(self, name):
        """
        Delete a variable.
        
        Args:
            name (str): The name of the variable to delete
            
        Returns:
            bool: True if the variable was deleted, False if it didn't exist
        """
        if name in self.variables:
            del self.variables[name]
            return True
        return False
    
    def clear(self):
        """
        Clear all variables.
        
        Returns:
            int: The number of variables that were cleared
        """
        count = len(self.variables)
        self.variables = {}
        return count
    
    def get_all(self):
        """
        Get all variables.
        
        Returns:
            dict: A dictionary of all variables
        """
        return self.variables.copy()
    
    def has(self, name):
        """
        Check if a variable exists.
        
        Args:
            name (str): The name of the variable
            
        Returns:
            bool: True if the variable exists, False otherwise
        """
        return name in self.variables
