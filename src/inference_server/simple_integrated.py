import asyncio
import logging
import os
import threading
import time

import gradio as gr
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

# Import our existing components
from inference_server.main import app as fastapi_app
from inference_server.main import session_manager

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_PORT = 7860
DEFAULT_TRANSPORT_SERVER_URL = os.getenv(
    "TRANSPORT_SERVER_URL", "http://localhost:8000"
)

# Global server thread
server_thread = None
server_started = False


def start_api_server_thread(port: int = 8001):
    """Start the API server in a background thread."""
    global server_thread, server_started

    if server_thread and server_thread.is_alive():
        return

    def run_server():
        global server_started
        logger.info(f"Starting AI server on port {port}")
        uvicorn.run(fastapi_app, host="localhost", port=port, log_level="warning")
        server_started = False

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    server_started = True

    # Wait a moment for server to start
    time.sleep(2)


def create_gradio(
    transport_server_url: str = DEFAULT_TRANSPORT_SERVER_URL,
) -> gr.Blocks:
    """Create an enhanced Gradio interface with step-by-step workflow."""
    server_manager = ServerManagement()

    custom_css = """
    .gradio-container {
        max-width: 1200px !important;
        margin: 0 auto !important;
        padding: 20px !important;
    }

    .main-header {
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        border-radius: 10px;
    }

    .main-header h1 {
        margin: 0;
        font-size: 2.5em;
        font-weight: bold;
    }

    .main-header p {
        margin: 10px 0 0 0;
        font-size: 1.1em;
        opacity: 0.8;
    }

    .status-display {
        font-family: monospace;
        font-size: 0.9em;
    }
    """

    with gr.Blocks(
        title="🤖 RobotHub AI Control Center",
        theme=gr.themes.Soft(),
        css=custom_css,
    ) as demo:
        # Main header
        with gr.Row():
            with gr.Column():
                gr.HTML("""
                <div class="main-header">
                    <h1>🤖 RobotHub AI Control Center</h1>
                    <p>Control your robot with AI using ACT (Action Chunking Transformer) models</p>
                </div>
                """)

        # Step 1: Server Status
        with gr.Group():
            gr.Markdown("## 📡 Step 1: AI Server Status")

            with gr.Row():
                with gr.Column(scale=3):
                    server_status_display = gr.Textbox(
                        label="Server Status",
                        value="✅ Integrated server ready",
                        interactive=False,
                        lines=2,
                        elem_classes="status-display",
                    )

                with gr.Column(scale=1, min_width=200):
                    check_status_btn = gr.Button(
                        "🔍 Check Status", variant="secondary", size="lg"
                    )

        # Step 2: Robot Setup
        with gr.Group():
            gr.Markdown("## 🤖 Step 2: Set Up Robot AI")

            with gr.Row():
                with gr.Column(scale=2):
                    session_name = gr.Textbox(
                        label="Session Name",
                        placeholder="my-robot-session",
                        value="my-robot-01",
                    )

                    model_path = gr.Textbox(
                        label="AI Model Path",
                        placeholder="LaetusH/act_so101_beyond",
                        value="LaetusH/act_so101_beyond",
                    )

                    camera_names = gr.Textbox(
                        label="Camera Names (comma-separated)",
                        placeholder="front, wrist, overhead",
                        value="front",
                    )

                    transport_server_url = gr.Textbox(
                        label="Transport Server URL",
                        placeholder="http://localhost:8000",
                        value=transport_server_url,
                    )

                    with gr.Row():
                        create_btn = gr.Button(
                            "🎯 Create & Start AI Control", variant="primary", size="lg"
                        )

                with gr.Column(scale=2):
                    setup_result = gr.Textbox(
                        label="Setup Result",
                        lines=12,
                        interactive=False,
                        placeholder="Click 'Create & Start AI Control' to begin...",
                        elem_classes="status-display",
                    )

        # Step 3: Control Session
        with gr.Group():
            gr.Markdown("## 🎮 Step 3: Control Session")

            with gr.Row():
                with gr.Column(scale=2):
                    session_id_input = gr.Textbox(
                        label="Session ID",
                        placeholder="Will be auto-filled",
                        interactive=True,
                    )

                with gr.Column(scale=2), gr.Row():
                    start_btn = gr.Button("▶️ Start", variant="primary")
                    stop_btn = gr.Button("⏹️ Stop", variant="secondary")
                    status_btn = gr.Button("📊 Status", variant="secondary")

            session_status_display = gr.Textbox(
                label="Session Status",
                lines=10,
                interactive=False,
                elem_classes="status-display",
            )

        # Event handlers
        check_status_btn.click(
            fn=server_manager.check_server_status,
            outputs=[server_status_display],
        )

        create_btn.click(
            fn=server_manager.create_and_start_session,
            inputs=[session_name, model_path, camera_names, transport_server_url],
            outputs=[session_id_input, setup_result],
        )

        start_btn.click(
            fn=server_manager.start_session,
            inputs=[session_id_input],
            outputs=[session_status_display],
        )

        stop_btn.click(
            fn=server_manager.stop_session,
            inputs=[session_id_input],
            outputs=[session_status_display],
        )

        status_btn.click(
            fn=server_manager.get_session_status,
            inputs=[session_id_input],
            outputs=[session_status_display],
        )

        # Auto-refresh on load
        demo.load(server_manager.check_server_status, outputs=[server_status_display])

        # Add helpful instructions
        with gr.Group():
            gr.Markdown("""
            ---
            ### 📖 Quick Guide:
            1. **Server Status**: The integrated server is ready by default
            2. **Configure Your Robot**: Enter your model path and camera setup (Step 2)
            3. **Create Session**: Click "Create & Start AI Control" to begin
            4. **Monitor & Control**: Use Step 3 to start/stop and monitor your session

            💡 **Tips**:
            - Make sure your ACT model path exists before creating a session
            - Camera names should match your robot's camera configuration
            - Session will automatically start after creation
            - All components run in a single integrated process for simplicity
            """)

    return demo


class ServerManagement:
    """Enhanced session management with better error handling and status display."""

    def check_server_status(self):
        """Check the status of the integrated server."""
        try:
            # Since we're running integrated, we can check session_manager directly
            if hasattr(session_manager, "sessions"):
                active_count = len([
                    s
                    for s in session_manager.sessions.values()
                    if s.status == "running"
                ])
                total_count = len(session_manager.sessions)
                return f"✅ Integrated server running - {active_count}/{total_count} sessions active"
            return "✅ Integrated server ready - No active sessions"
        except Exception as e:
            return f"⚠️ Server check failed: {e!s}"

    def create_and_start_session(
        self, session_name: str, model_path: str, camera_names: str, transport_url: str
    ):
        """Create and start a new session with enhanced error handling."""
        try:
            # Input validation
            if not session_name.strip():
                return "", "❌ Session name cannot be empty"

            if not model_path.strip():
                return "", "❌ Model path cannot be empty"

            # Parse camera names
            cameras = [c.strip() for c in camera_names.split(",") if c.strip()]
            if not cameras:
                cameras = ["front"]

            # Create session directly using session_manager
            # Use asyncio.run to handle the async function

            try:
                room_info = asyncio.run(
                    session_manager.create_session(
                        session_id=session_name.strip(),
                        policy_path=model_path.strip(),
                        camera_names=cameras,
                        transport_server_url=transport_url.strip(),
                    )
                )

                # Start the session
                asyncio.run(session_manager.start_inference(session_name.strip()))

                success_msg = f"""✅ Session '{session_name}' created and started!

📡 Configuration:
• Model: {model_path}
• Cameras: {", ".join(cameras)}
• Transport: {transport_url}
• Workspace: {room_info["workspace_id"]}

🏠 Rooms Created:
• Camera rooms: {", ".join(f"{k}:{v}" for k, v in room_info["camera_room_ids"].items())}
• Joint input: {room_info["joint_input_room_id"]}
• Joint output: {room_info["joint_output_room_id"]}

🤖 Ready for robot control!"""

                return session_name.strip(), success_msg

            except Exception as e:
                error_msg = f"❌ Error creating/starting session: {e!s}"
                logger.exception(error_msg)
                return "", error_msg

        except Exception as e:
            error_msg = f"❌ Error creating session: {e!s}"
            logger.exception(error_msg)
            return "", error_msg

    def start_session(self, session_id: str):
        """Start an existing session with better error handling."""
        if not session_id.strip():
            return "⚠️ Please provide a session ID"

        try:
            import asyncio

            asyncio.run(session_manager.start_inference(session_id.strip()))
            return f"✅ Session `{session_id}` started successfully!"
        except Exception as e:
            error_msg = f"❌ Failed to start session: {e!s}"
            logger.exception(error_msg)
            return error_msg

    def stop_session(self, session_id: str):
        """Stop an existing session with better error handling."""
        if not session_id.strip():
            return "⚠️ Please provide a session ID"

        try:
            import asyncio

            asyncio.run(session_manager.stop_inference(session_id.strip()))
            return f"⏹️ Session `{session_id}` stopped successfully!"
        except Exception as e:
            error_msg = f"❌ Failed to stop session: {e!s}"
            logger.exception(error_msg)
            return error_msg

    def get_session_status(self, session_id: str):
        """Get detailed session status with enhanced display."""
        if not session_id.strip():
            return "⚠️ Please provide a session ID"

        try:
            # Access the session directly from session_manager.sessions
            session_id_clean = session_id.strip()
            if session_id_clean not in session_manager.sessions:
                return f"❌ Session `{session_id}` not found"

            # Get session and call its get_status method
            session = session_manager.sessions[session_id_clean]
            status = session.get_status()

            # Enhanced status display with emojis
            status_emoji = {
                "running": "🟢",
                "ready": "🟡",
                "stopped": "🔴",
                "initializing": "🟠",
                "error": "❌",
                "timeout": "⏰",
            }.get(status.get("status", "unknown"), "⚪")

            status_msg = f"""{status_emoji} Session: `{session_id}`

**Status:** {status.get("status", "Unknown").upper()}
**Model:** {status.get("policy_path", "N/A")}
**Policy Type:** {status.get("policy_type", "N/A")}
**Cameras:** {", ".join(status.get("camera_names", []))}
**Workspace:** {status.get("workspace_id", "N/A")}

📊 **Performance:**
• Inferences: {status.get("stats", {}).get("inference_count", 0)}
• Commands sent: {status.get("stats", {}).get("commands_sent", 0)}
• Queue length: {status.get("stats", {}).get("actions_in_queue", 0)}
• Errors: {status.get("stats", {}).get("errors", 0)}

🔧 **Data Flow:**
• Images received: {status.get("stats", {}).get("images_received", {})}
• Joint states received: {status.get("stats", {}).get("joints_received", 0)}

🏠 **Rooms:**
• Camera rooms: {", ".join(f"{k}:{v}" for k, v in status.get("rooms", {}).get("camera_room_ids", {}).items())}
• Joint input: {status.get("rooms", {}).get("joint_input_room_id", "N/A")}
• Joint output: {status.get("rooms", {}).get("joint_output_room_id", "N/A")}"""

            return status_msg

        except Exception as e:
            error_msg = f"❌ Error getting status: {e!s}"
            logger.exception(error_msg)
            return error_msg


def launch_simple_integrated_app(
    host: str = "localhost",
    port: int = DEFAULT_PORT,
    share: bool = False,
    transport_server_url: str = DEFAULT_TRANSPORT_SERVER_URL,
):
    """Launch the enhanced integrated application with both FastAPI and Gradio."""
    print(f"🚀 Starting enhanced integrated app on {host}:{port}")
    print(f"🎨 Gradio UI: http://{host}:{port}/")
    print(f"📖 FastAPI Docs: http://{host}:{port}/api/docs")
    print(f"🔄 Health Check: http://{host}:{port}/api/health")
    print(f"🚌 Transport Server: {transport_server_url}")
    print("🔧 Enhanced direct session management + API access!")

    # Create enhanced Gradio demo
    demo = create_gradio(transport_server_url=transport_server_url)

    # Create main FastAPI app
    app = FastAPI(
        title="🤖 RobotHub AI Control Center",
        description="Enhanced Integrated ACT Model Inference Server with Web Interface",
        version="1.0.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount the FastAPI AI server under /api
    app.mount("/api", fastapi_app)

    # Mount Gradio at a subpath
    app = gr.mount_gradio_app(app, demo, path="/gradio")

    # Add custom root endpoint that redirects to /gradio/
    @app.get("/")
    def root_redirect():
        return RedirectResponse(url="/gradio/", status_code=302)

    # Launch with uvicorn
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    launch_simple_integrated_app()
