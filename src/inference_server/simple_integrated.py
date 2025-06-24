import logging
import threading
import time

import gradio as gr
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
        from inference_server.main import app

        try:
            uvicorn.run(app, host="localhost", port=port, log_level="warning")
        except Exception as e:
            logger.exception(f"API server error: {e}")
        finally:
            server_started = False

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait a moment for server to start
    time.sleep(2)
    server_started = True


class SimpleServerManager:
    """Direct access to session manager without HTTP calls."""

    def __init__(self):
        self.session_manager = session_manager

    async def create_and_start_session(
        self,
        session_id: str,
        policy_path: str,
        camera_names: str,
        arena_server_url: str,
    ) -> str:
        """Create and start a session directly."""
        try:
            cameras = [name.strip() for name in camera_names.split(",") if name.strip()]
            if not cameras:
                cameras = ["front"]

            # Create session directly
            room_info = await self.session_manager.create_session(
                session_id=session_id,
                policy_path=policy_path,
                camera_names=cameras,
                arena_server_url=arena_server_url,
            )

            # Start the session
            await self.session_manager.start_inference(session_id)

            # Format camera rooms more clearly
            camera_info = []
            for camera_name, room_id in room_info["camera_room_ids"].items():
                camera_info.append(f"  📹 **{camera_name.title()}**: `{room_id}`")

            return f"""## ✅ Session Created Successfully!

**Session ID**: `{session_id}`
**Status**: 🟢 **RUNNING** (inference active)

### 📡 Arena Connection Details:
**Workspace ID**: `{room_info["workspace_id"]}`

**Camera Rooms**:
{chr(10).join(camera_info)}

**Joint Communication**:
  📥 **Input**: `{room_info["joint_input_room_id"]}`
  📤 **Output**: `{room_info["joint_output_room_id"]}`

---
## 🤖 Ready for Robot Control!
Your robot can now connect to these rooms to start AI-powered control."""

        except Exception as e:
            return f"❌ Error: {e!s}"

    async def control_session(self, session_id: str, action: str) -> str:
        """Control a session directly."""
        if not session_id.strip():
            return "⚠️ No session ID provided"

        try:
            # Check current status
            if session_id not in self.session_manager.sessions:
                return f"❌ Session '{session_id}' not found"

            session = self.session_manager.sessions[session_id]
            current_status = session.status

            # Smart action handling
            if action == "start" and current_status == "running":
                return f"ℹ️ Session '{session_id}' is already running"
            if action == "stop" and current_status in {"stopped", "ready"}:
                return f"ℹ️ Session '{session_id}' is already stopped"

            # Perform action
            if action == "start":
                await self.session_manager.start_inference(session_id)
                return f"✅ Inference started for session {session_id}"
            if action == "stop":
                await self.session_manager.stop_inference(session_id)
                return f"✅ Inference stopped for session {session_id}"
            if action == "restart":
                await self.session_manager.restart_inference(session_id)
                return f"✅ Inference restarted for session {session_id}"
            return f"❌ Unknown action: {action}"

        except Exception as e:
            return f"❌ Error: {e!s}"

    async def get_session_status(self, session_id: str) -> str:
        """Get session status directly."""
        if not session_id.strip():
            return "⚠️ No session ID provided"

        try:
            if session_id not in self.session_manager.sessions:
                return f"❌ Session '{session_id}' not found"

            session_data = await self.session_manager.get_session_status(session_id)
            session = session_data

            status_emoji = {
                "running": "🟢",
                "ready": "🟡",
                "stopped": "🔴",
                "initializing": "🟠",
            }.get(session["status"], "⚪")

            # Smart suggestions
            suggestions = ""
            if session["status"] == "running":
                suggestions = "\n\n### 💡 Smart Suggestion:\n**Session is active!** Use the '⏸️ Stop' button to pause inference."
            elif session["status"] in {"ready", "stopped"}:
                suggestions = "\n\n### 💡 Smart Suggestion:\n**Session is ready!** Use the '▶️ Start' button to begin inference."

            # Format camera names nicely
            camera_list = [f"**{cam.title()}**" for cam in session["camera_names"]]

            return f"""## {status_emoji} Session Status

**Session ID**: `{session_id}`
**Status**: {status_emoji} **{session["status"].upper()}**
**Model**: `{session["policy_path"]}`
**Cameras**: {", ".join(camera_list)}

### 📊 Performance Metrics:
| Metric | Value |
|--------|-------|
| 🧠 **Inferences** | {session["stats"]["inference_count"]} |
| 📤 **Commands Sent** | {session["stats"]["commands_sent"]} |
| 📋 **Queue Length** | {session["stats"]["actions_in_queue"]} actions |
| ❌ **Errors** | {session["stats"]["errors"]} |

### 🔧 Data Flow:
- 📹 **Images Received**: {session["stats"]["images_received"]}
- 🤖 **Joint States Received**: {session["stats"]["joints_received"]}
{suggestions}"""

        except Exception as e:
            return f"❌ Error: {e!s}"


def create_simple_gradio_interface() -> gr.Blocks:
    """Create a simple Gradio interface with direct session management."""
    server_manager = SimpleServerManager()

    with gr.Blocks(
        title="🤖 Robot AI Control Center",
        theme=gr.themes.Soft(),
        css=".gradio-container { max-width: 1200px !important; }",
    ) as demo:
        gr.Markdown("""
        # 🤖 Robot AI Control Center
        **Control your robot with AI using ACT models**

        *Integrated mode - FastAPI available at `/api/docs` for direct API access*
        """)

        # Server status
        with gr.Group():
            gr.Markdown("## 📡 API Status")
            gr.Markdown(
                value="""
                ✅ **FastAPI Server**: Available at `/api`
                📖 **API Documentation**: Available at `/api/docs`
                🔄 **Health Check**: Available at `/api/health`
                """,
                show_copy_button=True,
            )

        # Setup
        with gr.Group():
            gr.Markdown("## 🤖 Set Up Robot AI")

            with gr.Row():
                with gr.Column():
                    session_id_input = gr.Textbox(
                        label="Session Name", value="my-robot-01"
                    )
                    policy_path_input = gr.Textbox(
                        label="AI Model Path", value="./checkpoints/act_so101_beyond"
                    )
                    camera_names_input = gr.Textbox(label="Camera Names", value="front")
                    arena_server_url_input = gr.Textbox(
                        label="Arena Server URL",
                        value=DEFAULT_ARENA_SERVER_URL,
                        placeholder="http://localhost:8000",
                    )
                    create_btn = gr.Button(
                        "🎯 Create & Start AI Control", variant="primary"
                    )

                with gr.Column():
                    setup_result = gr.Markdown(
                        value="Ready to create your robot AI session...",
                        show_copy_button=True,
                        container=True,
                        height=300,
                    )

        # Control
        with gr.Group():
            gr.Markdown("## 🎮 Control Session")

            with gr.Row():
                current_session_input = gr.Textbox(label="Session ID")
                start_btn = gr.Button("▶️ Start", variant="primary")
                stop_btn = gr.Button("⏸️ Stop", variant="secondary")
                status_btn = gr.Button("📊 Status", variant="secondary")

            session_status_display = gr.Markdown(
                value="Click '📊 Status' to check session information...",
                show_copy_button=True,
                container=True,
                height=400,
            )

        # Event handlers
        async def create_session(
            session_id, policy_path, camera_names, arena_server_url
        ):
            result = await server_manager.create_and_start_session(
                session_id, policy_path, camera_names, arena_server_url
            )
            return result, session_id

        async def start_session(session_id):
            return await server_manager.control_session(session_id, "start")

        async def stop_session(session_id):
            return await server_manager.control_session(session_id, "stop")

        async def get_status(session_id):
            return await server_manager.get_session_status(session_id)

        # Connect events
        create_btn.click(
            create_session,
            inputs=[
                session_id_input,
                policy_path_input,
                camera_names_input,
                arena_server_url_input,
            ],
            outputs=[setup_result, current_session_input],
        )

        start_btn.click(
            start_session,
            inputs=[current_session_input],
            outputs=[session_status_display],
        )
        stop_btn.click(
            stop_session,
            inputs=[current_session_input],
            outputs=[session_status_display],
        )
        status_btn.click(
            get_status, inputs=[current_session_input], outputs=[session_status_display]
        )

        gr.Markdown("""
        ### 💡 Tips:
        - 🟢 **RUNNING**: Session actively doing inference
        - 🟡 **READY**: Session created but not started
        - 🔴 **STOPPED**: Session paused

        ### 🚀 API Access:
        - **FastAPI Docs**: Visit `/api/docs` for interactive API documentation
        - **Direct API**: Use `/api/sessions` endpoints for programmatic access
        - **Health Check**: `/api/health` shows server status
        - **OpenAPI Schema**: Available at `/api/openapi.json`
        """)

    return demo


def create_integrated_app() -> FastAPI:
    """Create integrated FastAPI app with Gradio mounted and API at /api."""
    # Create main FastAPI app
    main_app = FastAPI(
        title="🤖 Robot AI Control Center",
        description="Integrated ACT Model Inference Server with Web Interface",
        version="1.0.0",
    )

    # Add CORS middleware
    main_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount the FastAPI AI server under /api
    main_app.mount("/api", fastapi_app)

    # Create and mount Gradio interface
    gradio_app = create_simple_gradio_interface()

    # Mount Gradio as the main interface
    main_app = gr.mount_gradio_app(main_app, gradio_app, path="/")

    return main_app


def launch_simple_integrated_app(
    host: str = "localhost", port: int = DEFAULT_PORT, share: bool = False
):
    """Launch the integrated application with both FastAPI and Gradio."""
    print(f"🚀 Starting integrated app on {host}:{port}")
    print(f"🎨 Gradio UI: http://{host}:{port}/")
    print(f"📖 FastAPI Docs: http://{host}:{port}/api/docs")
    print(f"🔄 Health Check: http://{host}:{port}/api/health")
    print("🔧 Direct session management + API access!")

    # Create integrated app
    app = create_integrated_app()

    # Launch with uvicorn
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    launch_simple_integrated_app()
