import logging
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
DEFAULT_ARENA_SERVER_URL = "http://localhost:8000"

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
        try:
            # Import here to avoid circular imports
            from inference_server.main import app

            logger.info(f"Starting AI server on port {port}")
            uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
        except Exception as e:
            logger.exception(f"Failed to start AI server: {e}")
        finally:
            server_started = False

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    server_started = True

    # Wait a moment for server to start
    time.sleep(2)


def create_simple_gradio_interface() -> gr.Blocks:
    """Create a simple Gradio interface with direct session management."""
    server_manager = SimpleServerManager()

    with gr.Blocks(
        title="🤖 Robot AI Control Center",
        theme=gr.themes.Soft(),
        css=".gradio-container { max-width: 1200px !important; }",
        fill_height=True,
    ) as demo:
        gr.Markdown("# 🤖 Robot AI Control Center")
        gr.Markdown("*Real-time ACT Model Inference for Robot Control*")

        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("## 🚀 Set Up Robot AI")

                with gr.Group():
                    session_name = gr.Textbox(
                        label="Session Name",
                        placeholder="my-robot-01",
                        value="default-session",
                    )
                    model_path = gr.Textbox(
                        label="AI Model Path",
                        placeholder="./checkpoints/act_so101_beyond",
                        value="./checkpoints/act_so101_beyond",
                    )
                    camera_names = gr.Textbox(
                        label="Camera Names (comma-separated)",
                        placeholder="front,wrist,overhead",
                        value="front,wrist",
                    )

                create_btn = gr.Button(
                    "🎯 Create & Start AI Control", variant="primary"
                )

            with gr.Column(scale=1):
                gr.Markdown("## 📊 Control Session")

                session_id_input = gr.Textbox(
                    label="Session ID",
                    placeholder="Will be auto-filled",
                    interactive=False,
                )

                with gr.Row():
                    start_btn = gr.Button("▶️ Start", variant="secondary")
                    stop_btn = gr.Button("⏹️ Stop", variant="secondary")
                    status_btn = gr.Button("📈 Status", variant="secondary")

        with gr.Row():
            output_display = gr.Markdown("### Ready to create AI session...")

        # Event handlers
        create_btn.click(
            fn=server_manager.create_and_start_session,
            inputs=[session_name, model_path, camera_names],
            outputs=[session_id_input, output_display],
        )

        start_btn.click(
            fn=server_manager.start_session,
            inputs=[session_id_input],
            outputs=[output_display],
        )

        stop_btn.click(
            fn=server_manager.stop_session,
            inputs=[session_id_input],
            outputs=[output_display],
        )

        status_btn.click(
            fn=server_manager.get_session_status,
            inputs=[session_id_input],
            outputs=[output_display],
        )

    return demo


class SimpleServerManager:
    """Direct session management without HTTP API calls."""

    def create_and_start_session(self, name: str, model_path: str, camera_names: str):
        """Create and start a new session directly."""
        try:
            # Parse camera names
            cameras = [c.strip() for c in camera_names.split(",") if c.strip()]

            # Create session directly using session_manager
            session_data = {
                "name": name,
                "model_path": model_path,
                "arena_server_url": DEFAULT_ARENA_SERVER_URL,
                "workspace_id": "default_workspace",
                "room_id": f"room_{name}",
                "camera_names": cameras,
            }

            session_id = session_manager.create_session(session_data)
            session_manager.start_session(session_id)

            success_msg = f"""
### ✅ Success!
**Session ID:** `{session_id}`
**Status:** Running
**Model:** {model_path}
**Cameras:** {", ".join(cameras)}

🎉 AI control is now active!
"""
            return session_id, success_msg

        except Exception as e:
            error_msg = f"""
### ❌ Error
Failed to create session: {e!s}

Please check your model path and try again.
"""
            return "", error_msg

    def start_session(self, session_id: str):
        """Start an existing session."""
        if not session_id:
            return "⚠️ Please provide a session ID"

        try:
            session_manager.start_session(session_id)
            return f"✅ Session `{session_id}` started successfully!"
        except Exception as e:
            return f"❌ Failed to start session: {e!s}"

    def stop_session(self, session_id: str):
        """Stop an existing session."""
        if not session_id:
            return "⚠️ Please provide a session ID"

        try:
            session_manager.stop_session(session_id)
            return f"⏹️ Session `{session_id}` stopped successfully!"
        except Exception as e:
            return f"❌ Failed to stop session: {e!s}"

    def get_session_status(self, session_id: str):
        """Get detailed session status."""
        if not session_id:
            return "⚠️ Please provide a session ID"

        try:
            status = session_manager.get_session_status(session_id)
            if not status:
                return f"❌ Session `{session_id}` not found"

            status_msg = f"""
### 📊 Session Status: `{session_id}`

**State:** {status.get("state", "Unknown")}
**Model:** {status.get("model_path", "N/A")}
**Inferences:** {status.get("total_inferences", 0)}
**Commands Sent:** {status.get("commands_sent", 0)}
**Errors:** {status.get("errors", 0)}

**Performance:**
- Queue Length: {status.get("queue_length", 0)}
- Last Update: {status.get("last_update", "Never")}
"""
            return status_msg

        except Exception as e:
            return f"❌ Failed to get status: {e!s}"


def launch_simple_integrated_app(
    host: str = "localhost", port: int = DEFAULT_PORT, share: bool = False
):
    """Launch the integrated application with both FastAPI and Gradio."""
    print(f"🚀 Starting integrated app on {host}:{port}")
    print(f"🎨 Gradio UI: http://{host}:{port}/")
    print(f"📖 FastAPI Docs: http://{host}:{port}/api/docs")
    print(f"🔄 Health Check: http://{host}:{port}/api/health")
    print("🔧 Direct session management + API access!")

    # Create Gradio demo first
    demo = create_simple_gradio_interface()

    # Create main FastAPI app
    app = FastAPI(
        title="🤖 Robot AI Control Center",
        description="Integrated ACT Model Inference Server with Web Interface",
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

    # Mount the FastAPI AI server under /api FIRST
    app.mount("/api", fastapi_app)

    # Mount Gradio at a subpath to avoid the root redirect issue
    app = gr.mount_gradio_app(app, demo, path="/gradio")

    # Add custom root endpoint that redirects to /gradio/ (with trailing slash)
    @app.get("/")
    async def root():
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
