import argparse
import logging
import sys

import uvicorn

from inference_server.export_openapi import export_openapi_schema
from inference_server.simple_integrated import launch_simple_integrated_app


def setup_logging(debug: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def launch_server_only(host: str = "localhost", port: int = 8001, reload: bool = True):
    """Launch only the AI server."""
    print(f"🚀 Starting RobotHub Inference Server on {host}:{port}")
    uvicorn.run(
        "inference_server.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


def launch_integrated_app(
    host: str = "localhost", port: int = 7860, share: bool = False, debug: bool = False
):
    """Launch the integrated app (UI + Server)."""
    print(f"🎨 Starting Integrated RobotHub App on {host}:{port}")
    setup_logging(debug)
    launch_simple_integrated_app(host=host, port=port, share=share)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RobotHub Inference Server CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch integrated app (recommended)
  python -m inference_server.cli

  # Launch only the server
  python -m inference_server.cli --server-only

  # Launch with custom ports
  python -m inference_server.cli --port 7861

  # Launch with public sharing (Gradio)
  python -m inference_server.cli --share

  # Export OpenAPI schema
  python -m inference_server.cli --export-openapi

  # Export as YAML
  python -m inference_server.cli --export-openapi --export-format yaml
        """,
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--server-only", action="store_true", help="Launch only the AI server"
    )

    # Server configuration
    parser.add_argument(
        "--server-host", default="localhost", help="AI server host (default: localhost)"
    )
    parser.add_argument(
        "--server-port", type=int, default=8001, help="AI server port (default: 8001)"
    )
    parser.add_argument(
        "--no-reload", action="store_true", help="Disable auto-reload for server"
    )

    # App configuration
    parser.add_argument(
        "--host", default="localhost", help="App host (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=7860, help="App port (default: 7860)"
    )
    parser.add_argument(
        "--share", action="store_true", help="Create public Gradio link"
    )

    # General options
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    # Export options
    mode_group.add_argument(
        "--export-openapi", action="store_true", help="Export OpenAPI schema to file"
    )
    parser.add_argument(
        "--export-format",
        choices=["json", "yaml"],
        default="json",
        help="OpenAPI export format (default: json)",
    )
    parser.add_argument(
        "--export-output",
        help="OpenAPI export output file (default: openapi.json or openapi.yaml)",
    )

    args = parser.parse_args()

    try:
        # Route to appropriate function
        if args.server_only:
            launch_server_only(
                host=args.server_host, port=args.server_port, reload=not args.no_reload
            )
        elif args.export_openapi:
            # Export OpenAPI schema
            output_file = args.export_output
            if output_file is None:
                output_file = f"openapi.{args.export_format}"

            print(f"📄 Exporting OpenAPI schema to {output_file}")
            export_openapi_schema(
                output_file=output_file, format_type=args.export_format
            )
        else:
            # Launch integrated app (default)
            print("🚀 Launching integrated RobotHub Inference Server + UI")
            launch_integrated_app(
                host=args.host, port=args.port, share=args.share, debug=args.debug
            )
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        raise e from e


if __name__ == "__main__":
    main()
