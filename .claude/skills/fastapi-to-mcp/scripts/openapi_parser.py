"""OpenAPI Schema Parser for FastAPI to MCP Conversion

Parses FastAPI OpenAPI schemas and generates MCP tool definitions.

Usage:
    python scripts/openapi_parser.py <openapi_json_path>
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ParameterSchema:
    """Parameter schema information."""
    name: str
    type: str
    required: bool
    default: Any = None
    description: Optional[str] = None
    enum: Optional[List[str]] = None
    max_length: Optional[int] = None
    min_length: Optional[int] = None


@dataclass
class EndpointInfo:
    """Endpoint information extracted from OpenAPI."""
    path: str
    method: str
    operation_id: str
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: List[ParameterSchema] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


class OpenAPIParser:
    """Parser for FastAPI OpenAPI schemas."""

    def __init__(self, openapi_schema: Dict[str, Any]):
        """Initialize parser with OpenAPI schema.

        Args:
            openapi_schema: OpenAPI 3.0+ schema dictionary
        """
        self.schema = openapi_schema
        self.endpoints: List[EndpointInfo] = []

    def parse(self) -> List[EndpointInfo]:
        """Parse OpenAPI schema and extract endpoint information.

        Returns:
            List of endpoint information
        """
        paths = self.schema.get("paths", {})
        components = self.schema.get("components", {})
        schemas = components.get("schemas", {})

        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue

                endpoint = self._parse_operation(path, method, operation, schemas)
                self.endpoints.append(endpoint)

        return self.endpoints

    def _parse_operation(
        self,
        path: str,
        method: str,
        operation: Dict[str, Any],
        schemas: Dict[str, Any]
    ) -> EndpointInfo:
        """Parse a single operation.

        Args:
            path: Endpoint path
            method: HTTP method
            operation: Operation object from OpenAPI
            schemas: Component schemas

        Returns:
            EndpointInfo object
        """
        # Extract basic info
        operation_id = operation.get("operationId", self._generate_operation_id(path, method))
        summary = operation.get("summary")
        description = operation.get("description")
        tags = operation.get("tags", [])

        # Parse parameters
        parameters = self._parse_parameters(operation, path)

        # Parse request body
        request_body = self._parse_request_body(operation, schemas)
        if request_body:
            parameters.extend(request_body)

        # Parse responses
        responses = self._parse_responses(operation, schemas)

        return EndpointInfo(
            path=path,
            method=method.upper(),
            operation_id=operation_id,
            summary=summary,
            description=description,
            parameters=parameters,
            responses=responses,
            tags=tags
        )

    def _parse_parameters(
        self,
        operation: Dict[str, Any],
        path: str
    ) -> List[ParameterSchema]:
        """Parse operation parameters.

        Args:
            operation: Operation object
            path: Endpoint path

        Returns:
            List of parameter schemas
        """
        parameters = []

        # Parse path parameters
        path_params = self._extract_path_params(path)
        for param in path_params:
            parameters.append(ParameterSchema(
                name=param,
                type="string",  # Default to string for path params
                required=True,
                description=f"Path parameter: {param}"
            ))

        # Parse query/header/cookie parameters
        for param in operation.get("parameters", []):
            param_schema = param.get("schema", {})
            parameters.append(ParameterSchema(
                name=param["name"],
                type=param_schema.get("type", "string"),
                required=param.get("required", False),
                default=param_schema.get("default"),
                description=param.get("description"),
                enum=param_schema.get("enum")
            ))

        return parameters

    def _parse_request_body(
        self,
        operation: Dict[str, Any],
        schemas: Dict[str, Any]
    ) -> List[ParameterSchema]:
        """Parse request body as parameters.

        Args:
            operation: Operation object
            schemas: Component schemas

        Returns:
            List of parameter schemas from request body
        """
        request_body = operation.get("requestBody")
        if not request_body:
            return []

        content = request_body.get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema", {})

        return self._parse_schema_properties(schema, schemas, request_body.get("required", False))

    def _parse_schema_properties(
        self,
        schema: Dict[str, Any],
        schemas: Dict[str, Any],
        parent_required: bool = False
    ) -> List[ParameterSchema]:
        """Parse schema properties into parameters.

        Args:
            schema: JSON schema
            schemas: Component schemas
            parent_required: Whether parent is required

        Returns:
            List of parameter schemas
        """
        parameters = []

        # Handle $ref
        if "$ref" in schema:
            ref_path = schema["$ref"].split("/")[-1]
            if ref_path in schemas:
                schema = schemas[ref_path]

        properties = schema.get("properties", {})
        required_fields = schema.get("required", [])

        for prop_name, prop_schema in properties.items():
            # Handle nested $ref
            if "$ref" in prop_schema:
                ref_path = prop_schema["$ref"].split("/")[-1]
                if ref_path in schemas:
                    prop_schema = schemas[ref_path]

            param_type = prop_schema.get("type", "string")

            # Map array types
            if param_type == "array":
                items_type = prop_schema.get("items", {}).get("type", "string")
                param_type = f"list[{items_type}]"

            parameters.append(ParameterSchema(
                name=prop_name,
                type=param_type,
                required=prop_name in required_fields,
                default=prop_schema.get("default"),
                description=prop_schema.get("description"),
                enum=prop_schema.get("enum"),
                max_length=prop_schema.get("maxLength"),
                min_length=prop_schema.get("minLength")
            ))

        return parameters

    def _parse_responses(
        self,
        operation: Dict[str, Any],
        schemas: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Parse operation responses.

        Args:
            operation: Operation object
            schemas: Component schemas

        Returns:
            Dictionary of response schemas by status code
        """
        responses = {}

        for status_code, response in operation.get("responses", {}).items():
            content = response.get("content", {})
            json_content = content.get("application/json", {})
            schema = json_content.get("schema", {})

            # Resolve $ref if present
            if "$ref" in schema:
                ref_path = schema["$ref"].split("/")[-1]
                if ref_path in schemas:
                    schema = schemas[ref_path]

            responses[status_code] = {
                "description": response.get("description"),
                "schema": schema
            }

        return responses

    def _extract_path_params(self, path: str) -> List[str]:
        """Extract path parameters from path string.

        Args:
            path: Path string like "/users/{user_id}/tasks/{task_id}"

        Returns:
            List of parameter names
        """
        import re
        return re.findall(r"\{([^}]+)\}", path)

    def _generate_operation_id(self, path: str, method: str) -> str:
        """Generate operation ID from path and method.

        Args:
            path: Endpoint path
            method: HTTP method

        Returns:
            Generated operation ID
        """
        # Convert /api/v1/users/{id} -> api_v1_users_id
        path_parts = path.strip("/").replace("{", "").replace("}", "").split("/")
        return f"{method.lower()}_{'_'.join(path_parts)}"

    def to_tool_name(self, endpoint: EndpointInfo) -> str:
        """Convert endpoint to MCP tool name.

        Args:
            endpoint: Endpoint information

        Returns:
            Tool name (e.g., "create_task", "list_tasks")
        """
        # Use operation ID if available
        if endpoint.operation_id:
            # Clean up operation ID
            return endpoint.operation_id.replace("-", "_").lower()

        # Generate from path and method
        path_parts = endpoint.path.strip("/").split("/")

        # Remove common prefixes
        path_parts = [p for p in path_parts if p not in ["api", "v1", "v2"]]

        # Get resource name (last non-param part)
        resource = None
        for part in reversed(path_parts):
            if not part.startswith("{"):
                resource = part
                break

        if not resource:
            resource = "item"

        # Map HTTP methods to action verbs
        method_map = {
            "GET": "list" if not any("{" in p for p in path_parts) else "get",
            "POST": "create",
            "PUT": "update",
            "DELETE": "delete",
            "PATCH": "update"
        }

        action = method_map.get(endpoint.method, endpoint.method.lower())

        return f"{action}_{resource}"

    def generate_tool_docstring(self, endpoint: EndpointInfo) -> str:
        """Generate docstring for MCP tool.

        Args:
            endpoint: Endpoint information

        Returns:
            Formatted docstring
        """
        lines = []

        # Summary or description
        if endpoint.summary:
            lines.append(endpoint.summary)
        elif endpoint.description:
            lines.append(endpoint.description.split("\n")[0])
        else:
            lines.append(f"{endpoint.method} {endpoint.path}")

        # Add full description if different from summary
        if endpoint.description and endpoint.description != endpoint.summary:
            lines.append("")
            lines.append(endpoint.description)

        # Parameters section
        if endpoint.parameters:
            lines.append("")
            lines.append("Args:")
            for param in endpoint.parameters:
                param_desc = param.description or param.name
                optional = "" if param.required else " (optional)"
                lines.append(f"    {param.name}: {param_desc}{optional}")

        # Returns section
        if "200" in endpoint.responses or "201" in endpoint.responses:
            lines.append("")
            lines.append("Returns:")
            response = endpoint.responses.get("200") or endpoint.responses.get("201")
            desc = response.get("description", "Response data")
            lines.append(f"    dict: {desc}")

        return "\n".join(lines)


def load_openapi_schema(path: str) -> Dict[str, Any]:
    """Load OpenAPI schema from file or URL.

    Args:
        path: Path to OpenAPI JSON file or URL

    Returns:
        OpenAPI schema dictionary
    """
    if path.startswith("http"):
        import httpx
        response = httpx.get(path)
        response.raise_for_status()
        return response.json()
    else:
        with open(path, "r") as f:
            return json.load(f)


def main():
    """CLI entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python openapi_parser.py <openapi_json_path>")
        print("\nExample:")
        print("  python openapi_parser.py http://localhost:8000/openapi.json")
        print("  python openapi_parser.py ./openapi.json")
        sys.exit(1)

    schema_path = sys.argv[1]

    try:
        print(f"Loading OpenAPI schema from: {schema_path}")
        schema = load_openapi_schema(schema_path)

        print(f"Parsing schema...")
        parser = OpenAPIParser(schema)
        endpoints = parser.parse()

        print(f"\nFound {len(endpoints)} endpoints:\n")

        for endpoint in endpoints:
            tool_name = parser.to_tool_name(endpoint)
            print(f"  {endpoint.method:6} {endpoint.path:40} -> {tool_name}")
            print(f"         Summary: {endpoint.summary or 'N/A'}")
            print(f"         Parameters: {len(endpoint.parameters)}")
            print()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
