import argparse
import logging
import sys
import threading
import time

from inference_server.ui import launch_ui


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


def launch_server_only(host: str = "0.0.0.0", port: int = 8001, reload: bool = True):
    """Launch only the AI server."""
    print(f"🚀 Starting Inference Server on {host}:{port}")

    try:
        import uvicorn

        from inference_server.main import app

        uvicorn.run(app, host=host, port=port, reload=reload, log_level="info")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)


def launch_ui_only(
    host: str = "localhost", port: int = 7860, share: bool = False, debug: bool = False
):
    """Launch only the Gradio UI."""
    print(f"🎨 Starting Gradio UI on {host}:{port}")

    setup_logging(debug)

    try:
        launch_ui(server_name=host, server_port=port, share=share)
    except KeyboardInterrupt:
        print("\n🛑 UI stopped by user")


def launch_both(
    server_host: str = "0.0.0.0",
    server_port: int = 8001,
    ui_host: str = "localhost",
    ui_port: int = 7860,
    share: bool = False,
    debug: bool = False,
):
    """Launch both the AI server and Gradio UI."""
    print("🚀 Starting Inference Server with Gradio UI")

    setup_logging(debug)

    try:
        print(f"📡 Starting AI Server on {server_host}:{server_port}")

        # Start server in a background thread
        def run_server():
            import uvicorn

            from inference_server.main import app

            uvicorn.run(
                app,
                host=server_host,
                port=server_port,
                log_level="warning",  # Reduce verbosity
            )

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # Give server time to start
        print("⏳ Waiting for server to start...")
        time.sleep(3)

        print("✅ Server started successfully")
        print(f"🎨 Starting Gradio UI on {ui_host}:{ui_port}")

        # Start the UI (this will block)
        launch_ui(server_name=ui_host, server_port=ui_port, share=share)

    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        print("✅ All services stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Inference Server CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch simple integrated app (recommended)
  python -m inference_server.cli --simple

  # Launch both server and UI (development)
  python -m inference_server.cli

  # Launch only the server
  python -m inference_server.cli --server-only

  # Launch only the UI (server must be running separately)
  python -m inference_server.cli --ui-only

  # Launch with custom ports
  python -m inference_server.cli --server-port 8002 --ui-port 7861

  # Launch with public sharing (Gradio)
  python -m inference_server.cli --share

  # Launch for deployment (recommended)
  python -m inference_server.cli --simple --host 0.0.0.0 --share

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
    mode_group.add_argument(
        "--ui-only", action="store_true", help="Launch only the Gradio UI"
    )
    mode_group.add_argument(
        "--simple",
        action="store_true",
        help="Launch simple integrated app (recommended)",
    )

    # Server configuration
    parser.add_argument(
        "--server-host", default="0.0.0.0", help="AI server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--server-port", type=int, default=8001, help="AI server port (default: 8001)"
    )
    parser.add_argument(
        "--no-reload", action="store_true", help="Disable auto-reload for server"
    )

    # UI configuration
    parser.add_argument(
        "--ui-host", default="localhost", help="Gradio UI host (default: localhost)"
    )
    parser.add_argument(
        "--ui-port", type=int, default=7860, help="Gradio UI port (default: 7860)"
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

    # Route to appropriate function
    if args.server_only:
        launch_server_only(
            host=args.server_host, port=args.server_port, reload=not args.no_reload
        )
    elif args.ui_only:
        launch_ui_only(
            host=args.ui_host, port=args.ui_port, share=args.share, debug=args.debug
        )
    elif args.simple:
        # Launch simple integrated app
        from inference_server.simple_integrated import (
            launch_simple_integrated_app,
        )

        print("🚀 Launching simple integrated Inference Server + UI")
        print("No mounting issues - direct session management!")
        launch_simple_integrated_app(
            host=args.ui_host, port=args.ui_port, share=args.share
        )
    elif args.export_openapi:
        # Export OpenAPI schema
        from inference_server.export_openapi import export_openapi_schema

        output_file = args.export_output
        if output_file is None:
            output_file = f"openapi.{args.export_format}"

        print(f"📄 Exporting OpenAPI schema to {output_file}")
        export_openapi_schema(output_file=output_file, format_type=args.export_format)
    else:
        # Launch both (default)
        launch_both(
            server_host=args.server_host,
            server_port=args.server_port,
            ui_host=args.ui_host,
            ui_port=args.ui_port,
            share=args.share,
            debug=args.debug,
        )


if __name__ == "__main__":
    main()
