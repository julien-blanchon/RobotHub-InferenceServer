import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from fastapi.openapi.utils import get_openapi


from inference_server.main import app


def create_custom_openapi_schema(app) -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    # Generate the base OpenAPI schema
    openapi_schema = get_openapi(
        title="RobotHub Inference Server",
        version="1.0.0",
        summary="ACT Model Inference Server for Real-time Robot Control",
        routes=app.routes,
        openapi_version="3.1.0",
    )

    # Add tags with descriptions for better organization
    openapi_schema["tags"] = [
        {"name": "Health", "description": "Health check and server status endpoints"},
        {
            "name": "Sessions",
            "description": "Inference session management - create, control, and monitor AI sessions",
        },
        {
            "name": "Control",
            "description": "Session control operations - start, stop, restart inference",
        },
        {
            "name": "Debug",
            "description": "Debug and monitoring endpoints for system diagnostics",
        },
    ]

    # Add security schemes if needed (for future authentication)
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
        "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
    }

    # Cache the schema
    app.openapi_schema = openapi_schema
    return openapi_schema


def export_openapi_schema(
    output_file: str | None = None, format_type: str = "json"
) -> dict[str, Any]:
    if format_type not in {"json", "yaml"}:
        msg = f"Unsupported format: {format_type}. Use 'json' or 'yaml'"
        raise ValueError(msg)

    # Get the FastAPI app and generate schema
    openapi_schema = create_custom_openapi_schema(app)

    # If no output file specified, return the schema
    if output_file is None:
        return openapi_schema

    # Ensure output directory exists
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save to file
    with output_path.open("w", encoding="utf-8") as f:
        if format_type == "json":
            json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
        else:  # yaml
            yaml.dump(
                openapi_schema,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )

    print(f"✅ OpenAPI schema exported to {output_path}")
    print(f"📄 Format: {format_type.upper()}")
    print(
        f"📊 Endpoints: {len([route for route in app.routes if hasattr(route, 'methods')])}"
    )

    return openapi_schema


def main():
    """CLI entry point for OpenAPI export."""
    parser = argparse.ArgumentParser(
        description="Export OpenAPI schema from Inference Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export as JSON (default)
  python -m inference_server.export_openapi

  # Export as YAML
  python -m inference_server.export_openapi --format yaml

  # Custom output file
  python -m inference_server.export_openapi --output api_schema.json

  # Specify both format and output
  python -m inference_server.export_openapi --format yaml --output docs/openapi.yaml
        """,
    )

    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output file path (default: openapi.json or openapi.yaml based on format)",
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "yaml"],
        default="json",
        help="Output format (default: json)",
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate the generated schema (requires openapi-spec-validator)",
    )

    parser.add_argument(
        "--print",
        action="store_true",
        help="Print the schema to stdout instead of saving to file",
    )

    args = parser.parse_args()

    # Determine output file if not specified
    if args.output is None and not args.print:
        args.output = f"openapi.{args.format}"

    try:
        # Export the schema
        if args.print:
            schema = export_openapi_schema(output_file=None, format_type=args.format)
            if args.format == "json":
                print(json.dumps(schema, indent=2, ensure_ascii=False))
            else:
                print(
                    yaml.dump(
                        schema,
                        default_flow_style=False,
                        allow_unicode=True,
                        sort_keys=False,
                    )
                )
        else:
            schema = export_openapi_schema(
                output_file=args.output, format_type=args.format
            )

        # Validate schema if requested
        if args.validate:
            try:
                from openapi_spec_validator import validate_spec
                validate_spec(schema)
                print("✅ Schema validation passed")
            except ImportError:
                print(
                    "⚠️ Validation skipped: install openapi-spec-validator for validation"
                )

    except KeyboardInterrupt:
        print("\n🛑 Export cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Export failed: {e}")
        raise e from e


if __name__ == "__main__":
    main()
