#!/usr/bin/env python3
"""
Main launcher for the RobotHub Inference Server

Integrated application that runs both FastAPI and Gradio on the same port.
- FastAPI API available at /api with full documentation
- Gradio UI available at the root path /
- Single process, single port - perfect for deployment!
"""

import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from inference_server.simple_integrated import launch_simple_integrated_app

if __name__ == "__main__":
    print("🤖 RobotHub Inference Server (Integrated)")
    print("FastAPI + Gradio on the same port!")
    print("API Documentation available at /api/docs")
    print("Press Ctrl+C to stop")
    print("-" * 50)

    # Parse simple command line args
    import argparse

    parser = argparse.ArgumentParser(
        description="Launch integrated RobotHub Inference Server with FastAPI + Gradio"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7860, help="Port to bind to")
    parser.add_argument(
        "--share", action="store_true", help="Create public Gradio link"
    )
    parser.add_argument(
        "--transport-server-url",
        default="http://localhost:8000",
        help="Transport server URL",
    )

    args = parser.parse_args()

    print(f"🚀 Starting on {args.host}:{args.port}")
    print(f"🎨 Gradio UI: http://{args.host}:{args.port}/")
    print(f"📖 API Docs: http://{args.host}:{args.port}/api/docs")
    print(f"🚌 Transport Server: {args.transport_server_url}")
    print()

    launch_simple_integrated_app(
        host=args.host,
        port=args.port,
        share=args.share,
        transport_server_url=args.transport_server_url,
    )
