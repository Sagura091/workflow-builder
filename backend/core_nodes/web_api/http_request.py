from typing import Dict, Any, Optional
import json
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class HttpRequest(BaseNode):
    """
    A core node for making HTTP requests to external APIs.
    
    This node can make various types of HTTP requests and process the responses.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.http_request",
            name="HTTP Request",
            version="1.0.0",
            description="Make HTTP requests to external APIs",
            author="Workflow Builder",
            category=NodeCategory.WEB_API,
            tags=["http", "api", "request", "web", "core"],
            inputs=[
                PortDefinition(
                    id="url",
                    name="URL",
                    type="string",
                    description="The URL to send the request to",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="headers",
                    name="Headers",
                    type="object",
                    description="Headers to include in the request",
                    required=False,
                    ui_properties={
                        "position": "left-center-top"
                    }
                ),
                PortDefinition(
                    id="params",
                    name="Query Params",
                    type="object",
                    description="Query parameters to include in the URL",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="body",
                    name="Body",
                    type="any",
                    description="Body to include in the request",
                    required=False,
                    ui_properties={
                        "position": "left-center-bottom"
                    }
                ),
                PortDefinition(
                    id="trigger",
                    name="Trigger",
                    type="trigger",
                    description="Trigger to send the request",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="response",
                    name="Response",
                    type="any",
                    description="The response data",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="status",
                    name="Status",
                    type="number",
                    description="The HTTP status code",
                    ui_properties={
                        "position": "right-center-top"
                    }
                ),
                PortDefinition(
                    id="headers",
                    name="Headers",
                    type="object",
                    description="The response headers",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="error",
                    name="Error",
                    type="string",
                    description="Error message if the request failed",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="method",
                    name="Method",
                    type="select",
                    description="The HTTP method to use",
                    required=True,
                    default_value="GET",
                    options=[
                        {"label": "GET", "value": "GET"},
                        {"label": "POST", "value": "POST"},
                        {"label": "PUT", "value": "PUT"},
                        {"label": "DELETE", "value": "DELETE"},
                        {"label": "PATCH", "value": "PATCH"},
                        {"label": "HEAD", "value": "HEAD"},
                        {"label": "OPTIONS", "value": "OPTIONS"}
                    ]
                ),
                ConfigField(
                    id="url",
                    name="URL",
                    type="string",
                    description="Default URL to send the request to",
                    required=False
                ),
                ConfigField(
                    id="headers",
                    name="Headers",
                    type="code",
                    description="Default headers to include in the request (JSON format)",
                    required=False,
                    default_value="{}"
                ),
                ConfigField(
                    id="body",
                    name="Body",
                    type="code",
                    description="Default body to include in the request (JSON format)",
                    required=False,
                    default_value="{}"
                ),
                ConfigField(
                    id="timeout",
                    name="Timeout",
                    type="number",
                    description="Request timeout in seconds",
                    required=False,
                    default_value=30
                ),
                ConfigField(
                    id="parse_json",
                    name="Parse JSON",
                    type="boolean",
                    description="Whether to parse the response as JSON",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    id="follow_redirects",
                    name="Follow Redirects",
                    type="boolean",
                    description="Whether to follow redirects",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    id="auth_type",
                    name="Authentication Type",
                    type="select",
                    description="Type of authentication to use",
                    required=False,
                    default_value="none",
                    options=[
                        {"label": "None", "value": "none"},
                        {"label": "Basic", "value": "basic"},
                        {"label": "Bearer Token", "value": "bearer"},
                        {"label": "API Key", "value": "api_key"}
                    ]
                ),
                ConfigField(
                    id="username",
                    name="Username",
                    type="string",
                    description="Username for basic authentication",
                    required=False
                ),
                ConfigField(
                    id="password",
                    name="Password",
                    type="string",
                    description="Password for basic authentication",
                    required=False
                ),
                ConfigField(
                    id="token",
                    name="Token",
                    type="string",
                    description="Token for bearer authentication",
                    required=False
                ),
                ConfigField(
                    id="api_key",
                    name="API Key",
                    type="string",
                    description="API key for API key authentication",
                    required=False
                ),
                ConfigField(
                    id="api_key_name",
                    name="API Key Name",
                    type="string",
                    description="Name of the API key header or parameter",
                    required=False,
                    default_value="X-API-Key"
                ),
                ConfigField(
                    id="api_key_in",
                    name="API Key In",
                    type="select",
                    description="Where to include the API key",
                    required=False,
                    default_value="header",
                    options=[
                        {"label": "Header", "value": "header"},
                        {"label": "Query Parameter", "value": "query"}
                    ]
                )
            ],
            ui_properties={
                "color": "#e74c3c",
                "icon": "globe",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the HTTP request node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The response data
        """
        import requests
        
        # Get inputs
        input_url = inputs.get("url")
        input_headers = inputs.get("headers")
        input_params = inputs.get("params")
        input_body = inputs.get("body")
        trigger = inputs.get("trigger", False)
        
        # Get configuration
        method = config.get("method", "GET")
        config_url = config.get("url", "")
        config_headers_str = config.get("headers", "{}")
        config_body_str = config.get("body", "{}")
        timeout = config.get("timeout", 30)
        parse_json = config.get("parse_json", True)
        follow_redirects = config.get("follow_redirects", True)
        auth_type = config.get("auth_type", "none")
        username = config.get("username", "")
        password = config.get("password", "")
        token = config.get("token", "")
        api_key = config.get("api_key", "")
        api_key_name = config.get("api_key_name", "X-API-Key")
        api_key_in = config.get("api_key_in", "header")
        
        # Parse config JSON
        try:
            config_headers = json.loads(config_headers_str)
            config_body = json.loads(config_body_str)
        except json.JSONDecodeError:
            config_headers = {}
            config_body = {}
        
        # Use input values if provided, otherwise use config
        url = input_url if input_url is not None else config_url
        
        # Merge headers (input headers take precedence)
        headers = {}
        if config_headers:
            headers.update(config_headers)
        if input_headers:
            headers.update(input_headers)
        
        # Use input body if provided, otherwise use config
        body = input_body if input_body is not None else config_body
        
        # Use input params if provided
        params = input_params if input_params is not None else {}
        
        # Initialize outputs
        response_data = None
        status_code = 0
        response_headers = {}
        error = None
        
        # Check if URL is provided
        if not url:
            error = "No URL provided"
            return {
                "response": None,
                "status": 0,
                "headers": {},
                "error": error
            }
        
        try:
            # Apply authentication
            auth = None
            if auth_type == "basic":
                auth = (username, password)
            elif auth_type == "bearer":
                headers["Authorization"] = f"Bearer {token}"
            elif auth_type == "api_key":
                if api_key_in == "header":
                    headers[api_key_name] = api_key
                else:  # query
                    params[api_key_name] = api_key
            
            # Prepare request arguments
            request_kwargs = {
                "url": url,
                "headers": headers,
                "params": params,
                "timeout": timeout,
                "allow_redirects": follow_redirects
            }
            
            # Add auth if provided
            if auth:
                request_kwargs["auth"] = auth
            
            # Add body for appropriate methods
            if method in ["POST", "PUT", "PATCH"]:
                if isinstance(body, dict) or isinstance(body, list):
                    # JSON body
                    request_kwargs["json"] = body
                elif isinstance(body, str):
                    # String body
                    request_kwargs["data"] = body
                else:
                    # Other body types
                    request_kwargs["data"] = body
            
            # Send request
            response = requests.request(method, **request_kwargs)
            
            # Get response data
            status_code = response.status_code
            response_headers = dict(response.headers)
            
            # Parse response
            if parse_json and "application/json" in response.headers.get("Content-Type", ""):
                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    response_data = response.text
            else:
                response_data = response.text
        
        except requests.exceptions.Timeout:
            error = f"Request timed out after {timeout} seconds"
        except requests.exceptions.ConnectionError:
            error = "Connection error"
        except requests.exceptions.RequestException as e:
            error = str(e)
        except Exception as e:
            error = str(e)
        
        return {
            "response": response_data,
            "status": status_code,
            "headers": response_headers,
            "error": error
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        method = config.get("method", "")
        if not method:
            return "Method is required"
        
        # Validate timeout
        try:
            timeout = float(config.get("timeout", 30))
            if timeout <= 0:
                return "Timeout must be a positive number"
        except (ValueError, TypeError):
            return "Timeout must be a number"
        
        # Validate JSON
        headers_str = config.get("headers", "{}")
        body_str = config.get("body", "{}")
        
        try:
            json.loads(headers_str)
        except json.JSONDecodeError:
            return "Headers must be valid JSON"
        
        try:
            json.loads(body_str)
        except json.JSONDecodeError:
            return "Body must be valid JSON"
        
        # Validate authentication
        auth_type = config.get("auth_type", "none")
        
        if auth_type == "basic":
            if not config.get("username", ""):
                return "Username is required for basic authentication"
        elif auth_type == "bearer":
            if not config.get("token", ""):
                return "Token is required for bearer authentication"
        elif auth_type == "api_key":
            if not config.get("api_key", ""):
                return "API key is required for API key authentication"
            if not config.get("api_key_name", ""):
                return "API key name is required for API key authentication"
        
        return None
