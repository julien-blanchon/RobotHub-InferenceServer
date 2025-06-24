"""
Redesigned Gradio UI for Inference Server

This module provides a user-friendly, workflow-oriented interface.
"""

import subprocess
import time
from pathlib import Path

import gradio as gr
import httpx

# Configuration
DEFAULT_SERVER_HOST = "localhost"
DEFAULT_SERVER_PORT = 8001
DEFAULT_ARENA_SERVER_URL = "http://localhost:8000"


class AIServerManager:
    """Manages communication with the AI Server."""

    def __init__(
        self, server_url: str = f"http://{DEFAULT_SERVER_HOST}:{DEFAULT_SERVER_PORT}"
    ):
        self.server_url = server_url
        self.server_process: subprocess.Popen | None = None

    async def check_server_health(self) -> tuple[bool, str]:
        """Check if the AI server is running and healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.server_url}/health")
                if response.status_code == 200:
                    data = response.json()
                    return (
                        True,
                        f"✅ Server running - {data['active_sessions']} sessions active",
                    )
                return False, f"❌ Server error: {response.status_code}"
        except Exception as e:
            return False, f"❌ Server not reachable: {e!s}"

    def start_server(self) -> str:
        """Start the AI server process using uv."""
        if self.server_process and self.server_process.poll() is None:
            return "⚠️ Server is already running"

        try:
            cmd = [
                "uv",
                "run",
                "uvicorn",
                "inference_server.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                str(DEFAULT_SERVER_PORT),
                "--reload",
            ]

            self.server_process = subprocess.Popen(
                cmd,
                cwd=Path(__file__).parent.parent.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            time.sleep(4)

            if self.server_process.poll() is None:
                return f"🚀 AI Server started on {self.server_url}"
            return "❌ Failed to start server - check your model path and dependencies"

        except Exception as e:
            return f"❌ Error starting server: {e!s}"

    async def create_and_start_session(
        self,
        session_id: str,
        policy_path: str,
        camera_names: str,
        arena_server_url: str,
        workspace_id: str | None = None,
    ) -> str:
        """Create and immediately start an inference session."""
        try:
            # Parse camera names
            cameras = [name.strip() for name in camera_names.split(",") if name.strip()]
            if not cameras:
                cameras = ["front"]

            request_data = {
                "session_id": session_id,
                "policy_path": policy_path,
                "camera_names": cameras,
                "arena_server_url": arena_server_url,
            }

            if workspace_id and workspace_id.strip():
                request_data["workspace_id"] = workspace_id.strip()

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Create session
                response = await client.post(
                    f"{self.server_url}/sessions", json=request_data
                )

                if response.status_code != 200:
                    error_detail = response.json().get("detail", "Unknown error")
                    return f"❌ Failed to create session: {error_detail}"

                data = response.json()

                # Immediately start inference
                start_response = await client.post(
                    f"{self.server_url}/sessions/{session_id}/start"
                )

                if start_response.status_code != 200:
                    error_detail = start_response.json().get("detail", "Unknown error")
                    return f"⚠️ Session created but failed to start: {error_detail}"

                return f"""✅ Session '{session_id}' created and started!

📡 Connection Details:
• Workspace: {data["workspace_id"]}
• Camera rooms: {", ".join(f"{k}:{v}" for k, v in data["camera_room_ids"].items())}
• Joint input room: {data["joint_input_room_id"]}
• Joint output room: {data["joint_output_room_id"]}

🤖 Ready for robot control!"""

        except Exception as e:
            return f"❌ Error: {e!s}"


# Initialize the server manager
server_manager = AIServerManager()


def create_main_interface() -> gr.Blocks:
    """Create the main user-friendly interface."""
    with gr.Blocks(title="🤖 Robot AI Control Center", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🤖 Robot AI Control Center

        **Control your robot with AI using ACT (Action Chunking Transformer) models**

        Follow the steps below to set up real-time AI control for your robot.
        """)

        # Step 1: Server Status
        with gr.Group():
            gr.Markdown("## 📡 Step 1: AI Server")

            with gr.Row():
                with gr.Column(scale=2):
                    server_status_display = gr.Textbox(
                        label="Server Status",
                        value="Checking server...",
                        interactive=False,
                        lines=2,
                    )

                with gr.Column(scale=1):
                    start_server_btn = gr.Button("🚀 Start Server", variant="primary")
                    check_health_btn = gr.Button("🔍 Check Status", variant="secondary")

        # Step 2: Robot Setup
        with gr.Group():
            gr.Markdown("## 🤖 Step 2: Set Up Robot AI")

            with gr.Row():
                with gr.Column():
                    session_id_input = gr.Textbox(
                        label="Session Name",
                        placeholder="my-robot-session",
                        value="my-robot-01",
                    )

                    policy_path_input = gr.Textbox(
                        label="AI Model Path",
                        placeholder="./checkpoints/act_so101_beyond",
                        value="./checkpoints/act_so101_beyond",
                    )

                    camera_names_input = gr.Textbox(
                        label="Camera Names (comma-separated)",
                        placeholder="front, wrist, overhead",
                        value="front",
                    )

                    arena_server_url_input = gr.Textbox(
                        label="Arena Server URL",
                        placeholder="http://localhost:8000",
                        value=DEFAULT_ARENA_SERVER_URL,
                    )

                    create_start_btn = gr.Button(
                        "🎯 Create & Start AI Control", variant="primary"
                    )

                with gr.Column():
                    setup_result = gr.Textbox(
                        label="Setup Result",
                        lines=10,
                        interactive=False,
                        placeholder="Click 'Create & Start AI Control' to begin...",
                    )

        # Control buttons
        with gr.Group():
            gr.Markdown("## 🎮 Step 3: Control Session")

            with gr.Row():
                current_session_input = gr.Textbox(
                    label="Session ID", placeholder="Enter session ID"
                )

                start_btn = gr.Button("▶️ Start", variant="primary")
                stop_btn = gr.Button("⏸️ Stop", variant="secondary")
                status_btn = gr.Button("📊 Status", variant="secondary")

            session_status_display = gr.Textbox(
                label="Session Status", lines=8, interactive=False
            )

        # Event Handlers
        def start_server_click():
            return server_manager.start_server()

        async def check_health_click():
            _is_healthy, message = await server_manager.check_server_health()
            return message

        async def create_start_session_click(
            session_id, policy_path, camera_names, arena_server_url
        ):
            result = await server_manager.create_and_start_session(
                session_id, policy_path, camera_names, arena_server_url
            )
            return result, session_id

        async def control_session(session_id, action):
            """Control a session (start/stop)."""
            if not session_id.strip():
                return "⚠️ No session ID provided"

            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    endpoint = f"/sessions/{session_id}/{action}"
                    response = await client.post(
                        f"{server_manager.server_url}{endpoint}"
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return f"✅ {result['message']}"
                    error_detail = response.json().get("detail", "Unknown error")
                    return f"❌ Failed to {action}: {error_detail}"
            except Exception as e:
                return f"❌ Error: {e!s}"

        async def get_session_status(session_id):
            """Get session status."""
            if not session_id.strip():
                return "⚠️ No session ID provided"

            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        f"{server_manager.server_url}/sessions/{session_id}"
                    )

                    if response.status_code == 200:
                        session = response.json()

                        status_emoji = {
                            "running": "🟢",
                            "ready": "🟡",
                            "stopped": "🔴",
                            "initializing": "🟠",
                        }.get(session["status"], "⚪")

                        return f"""{status_emoji} Session: {session_id}
Status: {session["status"].upper()}
Model: {session["policy_path"]}
Cameras: {", ".join(session["camera_names"])}

📊 Performance:
• Inferences: {session["stats"]["inference_count"]}
• Commands sent: {session["stats"]["commands_sent"]}
• Queue: {session["stats"]["actions_in_queue"]} actions
• Errors: {session["stats"]["errors"]}

🔧 Data flow:
• Images received: {session["stats"]["images_received"]}
• Joint states received: {session["stats"]["joints_received"]}"""
                    return f"❌ Session not found or error: {response.status_code}"
            except Exception as e:
                return f"❌ Error: {e!s}"

        # Connect events
        start_server_btn.click(start_server_click, outputs=[server_status_display])
        check_health_btn.click(check_health_click, outputs=[server_status_display])

        create_start_btn.click(
            create_start_session_click,
            inputs=[
                session_id_input,
                policy_path_input,
                camera_names_input,
                arena_server_url_input,
            ],
            outputs=[setup_result, current_session_input],
        )

        # Session control buttons - create proper async wrappers
        async def start_session_click(session_id):
            return await control_session(session_id, "start")

        async def stop_session_click(session_id):
            return await control_session(session_id, "stop")

        start_btn.click(
            start_session_click,
            inputs=[current_session_input],
            outputs=[session_status_display],
        )

        stop_btn.click(
            stop_session_click,
            inputs=[current_session_input],
            outputs=[session_status_display],
        )

        status_btn.click(
            get_session_status,
            inputs=[current_session_input],
            outputs=[session_status_display],
        )

        # Auto-refresh on load
        demo.load(check_health_click, outputs=[server_status_display])

        # Add helpful instructions
        gr.Markdown("""
        ---
        ### 📖 Quick Guide:
        1. **Start the Server**: Ensure the AI server is running (Step 1)
        2. **Configure Your Robot**: Enter your model path and camera setup (Step 2)
        3. **Create Session**: Click "Create & Start AI Control" to begin
        4. **Monitor & Control**: Use Step 3 to start/stop and monitor your session

        💡 **Tips**:
        - Make sure your ACT model path exists before creating a session
        - Camera names should match your robot's camera configuration
        - Session will automatically start after creation
        """)

    return demo


def launch_ui(
    server_name: str = "localhost", server_port: int = 7860, share: bool = False
) -> None:
    """Launch the redesigned UI."""
    demo = create_main_interface()
    demo.launch(
        server_name=server_name, server_port=server_port, share=share, show_error=True
    )


if __name__ == "__main__":
    launch_ui()
