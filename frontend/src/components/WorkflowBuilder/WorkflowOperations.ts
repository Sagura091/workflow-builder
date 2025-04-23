/**
 * WorkflowOperations.ts
 * 
 * This file contains utility functions for workflow operations like save, load, export, and import.
 */

import { Workflow } from '../../types';

/**
 * Save a workflow to local storage
 * 
 * @param workflow The workflow to save
 * @returns The ID of the saved workflow
 */
export const saveWorkflow = (workflow: Workflow): string => {
  // Generate a unique ID if one doesn't exist
  const workflowId = workflow.id || `workflow-${Date.now()}`;
  
  // Create a copy of the workflow with the ID
  const workflowToSave = {
    ...workflow,
    id: workflowId,
    lastSaved: new Date().toISOString()
  };
  
  // Save to local storage
  try {
    // Get existing workflows
    const existingWorkflowsJson = localStorage.getItem('workflows') || '{}';
    const existingWorkflows = JSON.parse(existingWorkflowsJson);
    
    // Add or update this workflow
    existingWorkflows[workflowId] = workflowToSave;
    
    // Save back to local storage
    localStorage.setItem('workflows', JSON.stringify(existingWorkflows));
    
    return workflowId;
  } catch (error) {
    console.error('Error saving workflow:', error);
    throw new Error(`Failed to save workflow: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

/**
 * Get all saved workflows from local storage
 * 
 * @returns An array of saved workflows
 */
export const getSavedWorkflows = (): Workflow[] => {
  try {
    // Get workflows from local storage
    const workflowsJson = localStorage.getItem('workflows') || '{}';
    const workflows = JSON.parse(workflowsJson);
    
    // Convert to array and sort by last saved date
    return Object.values(workflows).sort((a: any, b: any) => {
      return new Date(b.lastSaved).getTime() - new Date(a.lastSaved).getTime();
    });
  } catch (error) {
    console.error('Error getting saved workflows:', error);
    return [];
  }
};

/**
 * Load a workflow from local storage by ID
 * 
 * @param workflowId The ID of the workflow to load
 * @returns The loaded workflow or null if not found
 */
export const loadWorkflow = (workflowId: string): Workflow | null => {
  try {
    // Get workflows from local storage
    const workflowsJson = localStorage.getItem('workflows') || '{}';
    const workflows = JSON.parse(workflowsJson);
    
    // Return the requested workflow
    return workflows[workflowId] || null;
  } catch (error) {
    console.error('Error loading workflow:', error);
    return null;
  }
};

/**
 * Delete a workflow from local storage
 * 
 * @param workflowId The ID of the workflow to delete
 * @returns True if successful, false otherwise
 */
export const deleteWorkflow = (workflowId: string): boolean => {
  try {
    // Get workflows from local storage
    const workflowsJson = localStorage.getItem('workflows') || '{}';
    const workflows = JSON.parse(workflowsJson);
    
    // Remove the workflow
    if (workflows[workflowId]) {
      delete workflows[workflowId];
      
      // Save back to local storage
      localStorage.setItem('workflows', JSON.stringify(workflows));
      return true;
    }
    
    return false;
  } catch (error) {
    console.error('Error deleting workflow:', error);
    return false;
  }
};

/**
 * Export a workflow to a JSON file
 * 
 * @param workflow The workflow to export
 */
export const exportWorkflow = (workflow: Workflow): void => {
  try {
    // Create a JSON string from the workflow
    const workflowJson = JSON.stringify(workflow, null, 2);
    
    // Create a blob from the JSON
    const blob = new Blob([workflowJson], { type: 'application/json' });
    
    // Create a URL for the blob
    const url = URL.createObjectURL(blob);
    
    // Create a link element
    const link = document.createElement('a');
    link.href = url;
    link.download = `${workflow.name.replace(/\s+/g, '_')}_${Date.now()}.json`;
    
    // Append the link to the body
    document.body.appendChild(link);
    
    // Click the link
    link.click();
    
    // Remove the link
    document.body.removeChild(link);
    
    // Revoke the URL
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error exporting workflow:', error);
    throw new Error(`Failed to export workflow: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

/**
 * Import a workflow from a JSON file
 * 
 * @param file The file to import
 * @returns A promise that resolves to the imported workflow
 */
export const importWorkflowFromFile = (file: File): Promise<Workflow> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (event) => {
      try {
        if (event.target && typeof event.target.result === 'string') {
          const workflow = JSON.parse(event.target.result);
          resolve(workflow);
        } else {
          reject(new Error('Failed to read file'));
        }
      } catch (error) {
        reject(error);
      }
    };
    
    reader.onerror = () => {
      reject(new Error('Error reading file'));
    };
    
    reader.readAsText(file);
  });
};

/**
 * Create a workflow selection dialog
 * 
 * @param workflows Array of workflows to choose from
 * @returns A promise that resolves to the selected workflow ID or null if cancelled
 */
export const createWorkflowSelectionDialog = (workflows: Workflow[]): Promise<string | null> => {
  return new Promise((resolve) => {
    // Create modal container
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50';
    modal.style.zIndex = '9999';
    
    // Create modal content
    modal.innerHTML = `
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold text-gray-800">Select a Workflow</h2>
            <button id="close-modal" class="text-gray-500 hover:text-gray-700">
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <div class="max-h-96 overflow-y-auto">
            ${workflows.length > 0 
              ? workflows.map((workflow, index) => `
                <div class="workflow-item p-3 border-b border-gray-200 hover:bg-gray-50 cursor-pointer" data-id="${workflow.id}">
                  <div class="flex justify-between items-center">
                    <div>
                      <h3 class="font-medium text-gray-800">${workflow.name}</h3>
                      <p class="text-sm text-gray-500">
                        ${workflow.lastSaved 
                          ? `Last saved: ${new Date(workflow.lastSaved).toLocaleString()}`
                          : 'Not saved yet'}
                      </p>
                      <p class="text-xs text-gray-400">
                        ${workflow.nodes.length} nodes, ${workflow.connections.length} connections
                      </p>
                    </div>
                    <button class="delete-workflow px-2 py-1 text-red-600 hover:text-red-800 text-sm" data-id="${workflow.id}">
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </div>
              `).join('')
              : '<div class="p-4 text-center text-gray-500">No saved workflows found</div>'
            }
          </div>
          
          <div class="mt-6 flex justify-end">
            <button id="cancel-selection" class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 mr-2">
              Cancel
            </button>
          </div>
        </div>
      </div>
    `;
    
    // Add modal to body
    document.body.appendChild(modal);
    
    // Add event listeners
    const closeModal = () => {
      document.body.removeChild(modal);
      resolve(null);
    };
    
    // Close button
    const closeButton = modal.querySelector('#close-modal');
    if (closeButton) {
      closeButton.addEventListener('click', closeModal);
    }
    
    // Cancel button
    const cancelButton = modal.querySelector('#cancel-selection');
    if (cancelButton) {
      cancelButton.addEventListener('click', closeModal);
    }
    
    // Workflow selection
    const workflowItems = modal.querySelectorAll('.workflow-item');
    workflowItems.forEach(item => {
      item.addEventListener('click', (e) => {
        const target = e.currentTarget as HTMLElement;
        const workflowId = target.dataset.id;
        if (workflowId) {
          document.body.removeChild(modal);
          resolve(workflowId);
        }
      });
    });
    
    // Delete buttons
    const deleteButtons = modal.querySelectorAll('.delete-workflow');
    deleteButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.stopPropagation();
        const target = e.currentTarget as HTMLElement;
        const workflowId = target.dataset.id;
        if (workflowId && confirm('Are you sure you want to delete this workflow?')) {
          deleteWorkflow(workflowId);
          const item = modal.querySelector(`.workflow-item[data-id="${workflowId}"]`);
          if (item && item.parentNode) {
            item.parentNode.removeChild(item);
          }
          
          // If no workflows left, show message
          if (modal.querySelectorAll('.workflow-item').length === 0) {
            const container = modal.querySelector('.max-h-96');
            if (container) {
              container.innerHTML = '<div class="p-4 text-center text-gray-500">No saved workflows found</div>';
            }
          }
        }
      });
    });
  });
};
