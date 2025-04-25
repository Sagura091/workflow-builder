"""
Plugin Testing Router

This module provides API routes for the plugin testing framework.
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from typing import Dict, Any, List, Optional
import os
import tempfile
import shutil

from backend.app.controllers.plugin_testing_controller import PluginTestingController
from backend.app.services.plugin_loader import PluginLoader
from backend.app.dependencies import get_plugin_loader
from backend.app.models.responses import StandardResponse

# Create router
router = APIRouter(prefix="/plugin-testing", tags=["plugin-testing"])

# Dependency for PluginTestingController
def get_plugin_testing_controller(
    plugin_loader: PluginLoader = Depends(get_plugin_loader)
):
    """Get PluginTestingController instance."""
    return PluginTestingController(plugin_loader)

@router.get("/{plugin_id}/quality", response_model=StandardResponse)
async def check_plugin_quality(
    plugin_id: str,
    controller: PluginTestingController = Depends(get_plugin_testing_controller)
) -> StandardResponse:
    """
    Check the quality of a plugin.

    Args:
        plugin_id: ID of the plugin to check

    Returns:
        StandardResponse: Response containing the quality check results
    """
    try:
        result = controller.check_plugin_quality(plugin_id)
        return StandardResponse.success(data=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking plugin quality: {str(e)}"
        )

@router.get("/{plugin_id}/production-readiness", response_model=StandardResponse)
async def validate_plugin_production_readiness(
    plugin_id: str,
    controller: PluginTestingController = Depends(get_plugin_testing_controller)
) -> StandardResponse:
    """
    Validate if a plugin is ready for production.

    Args:
        plugin_id: ID of the plugin to validate

    Returns:
        StandardResponse: Response containing the validation results
    """
    try:
        result = controller.validate_plugin_production_readiness(plugin_id)
        return StandardResponse.success(data=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating plugin production readiness: {str(e)}"
        )

@router.get("/{plugin_id}/certification", response_model=StandardResponse)
async def certify_plugin(
    plugin_id: str,
    controller: PluginTestingController = Depends(get_plugin_testing_controller)
) -> StandardResponse:
    """
    Certify a plugin.

    Args:
        plugin_id: ID of the plugin to certify

    Returns:
        StandardResponse: Response containing the certification results
    """
    try:
        result = controller.certify_plugin(plugin_id)
        return StandardResponse.success(data=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error certifying plugin: {str(e)}"
        )

@router.post("/{plugin_id}/generate-tests", response_model=StandardResponse)
async def generate_plugin_tests(
    plugin_id: str,
    controller: PluginTestingController = Depends(get_plugin_testing_controller)
) -> StandardResponse:
    """
    Generate tests for a plugin.

    Args:
        plugin_id: ID of the plugin to generate tests for

    Returns:
        StandardResponse: Response containing the test generation results
    """
    try:
        result = controller.generate_plugin_tests(plugin_id)
        return StandardResponse.success(data=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating plugin tests: {str(e)}"
        )

@router.post("/{plugin_id}/run-tests", response_model=StandardResponse)
async def run_plugin_tests(
    plugin_id: str,
    controller: PluginTestingController = Depends(get_plugin_testing_controller)
) -> StandardResponse:
    """
    Run tests for a plugin.

    Args:
        plugin_id: ID of the plugin to run tests for

    Returns:
        StandardResponse: Response containing the test results
    """
    try:
        result = controller.run_plugin_tests(plugin_id)
        return StandardResponse.success(data=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running plugin tests: {str(e)}"
        )

@router.post("/test-external-plugin", response_model=StandardResponse)
async def test_external_plugin(
    plugin_file: UploadFile = File(...),
    controller: PluginTestingController = Depends(get_plugin_testing_controller)
) -> StandardResponse:
    """
    Test an external plugin.

    Args:
        plugin_file: The plugin file to test

    Returns:
        StandardResponse: Response containing the test results
    """
    try:
        # Create a temporary directory to store the plugin file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the plugin file
            plugin_path = os.path.join(temp_dir, plugin_file.filename)
            with open(plugin_path, "wb") as f:
                shutil.copyfileobj(plugin_file.file, f)

            # Test the plugin
            result = controller.test_external_plugin(plugin_path)

            return StandardResponse.success(data=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing external plugin: {str(e)}"
        )

@router.post("/import-external-plugin", response_model=StandardResponse)
async def import_external_plugin(
    plugin_file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    controller: PluginTestingController = Depends(get_plugin_testing_controller)
) -> StandardResponse:
    """
    Import an external plugin into the backend.

    Args:
        plugin_file: The plugin file to import
        category: Category to import the plugin into (optional)

    Returns:
        StandardResponse: Response containing the import results
    """
    try:
        # Create a temporary directory to store the plugin file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the plugin file
            plugin_path = os.path.join(temp_dir, plugin_file.filename)
            with open(plugin_path, "wb") as f:
                shutil.copyfileobj(plugin_file.file, f)

            # Import the plugin
            result = controller.import_external_plugin(plugin_path, category)

            return StandardResponse.success(data=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing external plugin: {str(e)}"
        )
