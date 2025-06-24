import asyncio
import contextlib
import logging
import time
from collections import deque

import numpy as np
from robohub_transport_server_client import RoboticsConsumer, RoboticsProducer
from robohub_transport_server_client.video import VideoConsumer, VideoProducer

from inference_server.models import get_inference_engine, list_supported_policies
from inference_server.models.joint_config import JointConfig

logger = logging.getLogger(__name__)


def busy_wait(seconds):
    """
    Precise timing function for consistent control loops.

    On some systems, asyncio.sleep is not accurate enough for
    control loops, so we use busy waiting for short delays.
    """
    if seconds > 0:
        end_time = asyncio.get_event_loop().time() + seconds
        while asyncio.get_event_loop().time() < end_time:
            pass


class InferenceSession:
    """
    A single inference session managing one model and its Arena connections.

    Handles joint values in NORMALIZED VALUES throughout the pipeline.
    Supports multiple camera streams with different camera names.
    Supports multiple policy types: ACT, Pi0, SmolVLA, Diffusion Policy.
    """

    def __init__(
        self,
        session_id: str,
        policy_path: str,
        camera_names: list[str],
        arena_server_url: str,
        workspace_id: str,
        camera_room_ids: dict[str, str],
        joint_input_room_id: str,
        joint_output_room_id: str,
        policy_type: str = "act",
        language_instruction: str | None = None,
    ):
        self.session_id = session_id
        self.policy_path = policy_path
        self.policy_type = policy_type.lower()
        self.camera_names = camera_names
        self.arena_server_url = arena_server_url
        self.language_instruction = language_instruction

        # Validate policy type
        if self.policy_type not in list_supported_policies():
            supported = list_supported_policies()
            msg = f"Unsupported policy type: {policy_type}. Supported: {supported}"
            raise ValueError(msg)

        # Workspace and Room IDs
        self.workspace_id = workspace_id
        self.camera_room_ids = camera_room_ids  # {camera_name: room_id}
        self.joint_input_room_id = joint_input_room_id
        self.joint_output_room_id = joint_output_room_id

        # Arena clients - multiple camera consumers
        self.camera_consumers: dict[str, VideoConsumer] = {}  # {camera_name: consumer}
        self.joint_input_consumer: RoboticsConsumer | None = None
        self.joint_output_producer: RoboticsProducer | None = None

        # Generic inference engine (supports all policy types)
        self.inference_engine = None

        # Session state
        self.status = "initializing"
        self.error_message: str | None = None
        self.inference_task: asyncio.Task | None = None

        # Data buffers - all in normalized values
        self.latest_images: dict[str, np.ndarray] = {}  # {camera_name: image}
        self.latest_joint_positions: np.ndarray | None = None
        # Complete joint state (always 6 joints) - initialized with zeros
        self.complete_joint_state: np.ndarray = np.zeros(6, dtype=np.float32)
        self.images_updated: dict[str, bool] = dict.fromkeys(camera_names, False)
        self.joints_updated = False

        # Action queue for proper chunking (important for ACT, optional for others)
        self.action_queue: deque = deque(maxlen=100)  # Adjust maxlen as needed
        self.n_action_steps = 10  # How many actions to use from each chunk

        # Memory optimization: Clear old actions periodically
        self.last_queue_cleanup = time.time()
        self.queue_cleanup_interval = 10.0  # seconds

        # Control frequency configuration (matches LeRobot defaults)
        self.control_frequency_hz = 20  # Hz - reduced from 30 to improve performance
        self.inference_frequency_hz = 2  # Hz - reduced from 3 to improve performance

        # Statistics
        self.stats = {
            "inference_count": 0,
            "images_received": dict.fromkeys(camera_names, 0),
            "joints_received": 0,
            "commands_sent": 0,
            "errors": 0,
            "actions_in_queue": 0,
            "policy_type": self.policy_type,
        }

        # Robot responsiveness tracking
        self.last_command_values: np.ndarray | None = None
        self.last_joint_check_time = time.time()

        # Session timeout management
        self.last_activity_time = time.time()
        self.timeout_seconds = 600  # 10 minutes
        self.timeout_check_task: asyncio.Task | None = None

    async def initialize(self):
        """Initialize the session by loading the model and setting up Arena connections."""
        logger.info(
            f"Initializing session {self.session_id} with policy type: {self.policy_type}, "
            f"cameras: {self.camera_names}"
        )

        # Initialize inference engine based on policy type
        engine_kwargs = {
            "policy_path": self.policy_path,
            "camera_names": self.camera_names,
        }

        # Add language instruction for policies that support it
        if (
            self.policy_type in {"pi0", "pi0fast", "smolvla"}
            and self.language_instruction
        ):
            engine_kwargs["language_instruction"] = self.language_instruction

        self.inference_engine = get_inference_engine(self.policy_type, **engine_kwargs)

        # Load the policy
        await self.inference_engine.load_policy()

        # Create Arena clients for each camera
        for camera_name in self.camera_names:
            self.camera_consumers[camera_name] = VideoConsumer(self.arena_server_url)

        self.joint_input_consumer = RoboticsConsumer(self.arena_server_url)
        self.joint_output_producer = RoboticsProducer(self.arena_server_url)

        # Set up callbacks
        self._setup_callbacks()

        # Connect to rooms
        await self._connect_to_rooms()

        # Start receiving video frames from all cameras
        for camera_name, consumer in self.camera_consumers.items():
            await consumer.start_receiving()
            logger.info(f"Started receiving frames for camera: {camera_name}")

        # Start timeout monitoring
        self.timeout_check_task = asyncio.create_task(self._timeout_monitor())

        self.status = "ready"
        logger.info(
            f"✅ Session {self.session_id} initialized successfully with {self.policy_type} policy "
            f"and {len(self.camera_names)} cameras"
        )

    def _setup_callbacks(self):
        """Set up callbacks for Arena clients."""

        def create_frame_callback(camera_name: str):
            """Create a frame callback for a specific camera."""

            def on_frame_received(frame_data):
                """Handle incoming camera frame from VideoConsumer."""
                try:
                    metadata = frame_data.metadata
                    width = metadata.get("width", 0)
                    height = metadata.get("height", 0)
                    format_type = metadata.get("format", "rgb24")

                    if format_type == "rgb24" and width > 0 and height > 0:
                        # Convert bytes to numpy array (server sends RGB format)
                        frame_bytes = frame_data.data

                        # Validate frame data size
                        expected_size = height * width * 3
                        if len(frame_bytes) != expected_size:
                            logger.warning(
                                f"Frame size mismatch for camera {camera_name}: "
                                f"expected {expected_size}, got {len(frame_bytes)}. Skipping frame."
                            )
                            self.stats["errors"] += 1
                            return

                        img_rgb = np.frombuffer(frame_bytes, dtype=np.uint8).reshape((
                            height,
                            width,
                            3,
                        ))

                        # Store as latest image for inference
                        self.latest_images[camera_name] = img_rgb
                        self.images_updated[camera_name] = True
                        self.stats["images_received"][camera_name] += 1
                        # Update activity time
                        self.last_activity_time = time.time()

                    else:
                        logger.debug(
                            f"Skipping invalid frame for camera {camera_name}: {format_type}, "
                            f"{width}x{height}"
                        )

                except Exception as e:
                    logger.exception(
                        f"Error processing frame for camera {camera_name}: {e}"
                    )
                    self.stats["errors"] += 1

            return on_frame_received

        # Set up frame callbacks for each camera
        for camera_name in self.camera_names:
            callback = create_frame_callback(camera_name)
            self.camera_consumers[camera_name].on_frame_update(callback)

        def on_joints_received(joints_data):
            """Handle incoming joint data from RoboticsConsumer."""
            try:
                joint_values = self._parse_joint_data(joints_data)
                if joint_values:
                    # Update complete joint state with received values
                    for i, value in enumerate(joint_values[:6]):  # Ensure max 6 joints
                        self.complete_joint_state[i] = value

                    self.latest_joint_positions = self.complete_joint_state.copy()
                    self.joints_updated = True
                    self.stats["joints_received"] += 1
                    # Update activity time
                    self.last_activity_time = time.time()

            except Exception as e:
                logger.exception(f"Error processing joint data: {e}")
                self.stats["errors"] += 1

        def on_error(error_msg):
            """Handle Arena client errors."""
            logger.error(
                f"Arena client error in session {self.session_id}: {error_msg}"
            )
            self.error_message = str(error_msg)
            self.stats["errors"] += 1

        # Set callbacks for RoboticsConsumer
        self.joint_input_consumer.on_joint_update(on_joints_received)
        self.joint_input_consumer.on_state_sync(on_joints_received)
        self.joint_input_consumer.on_error(on_error)

        # Set error callbacks for VideoConsumers
        for consumer in self.camera_consumers.values():
            consumer.on_error(on_error)

    def _parse_joint_data(self, joints_data) -> list[float]:
        """
        Parse joint data from Arena message.

        Expected format: dict with joint names as keys and normalized values.
        All values are already normalized from the training data pipeline.

        Args:
            joints_data: Joint data from Arena message

        Returns:
            List of 6 normalized joint values in LeRobot standard order

        """
        return JointConfig.parse_joint_data(joints_data, self.policy_type)

    def _get_joint_index(self, joint_name: str) -> int | None:
        """
        Get the index of a joint in the standard joint order.

        Args:
            joint_name: Name of the joint

        Returns:
            Index of the joint, or None if not found

        """
        return JointConfig.get_joint_index(joint_name)

    async def _connect_to_rooms(self):
        """Connect to all Arena rooms."""
        # Connect to camera rooms as consumer
        for camera_name, consumer in self.camera_consumers.items():
            room_id = self.camera_room_ids[camera_name]
            success = await consumer.connect(
                self.workspace_id, room_id, f"{self.session_id}-{camera_name}-consumer"
            )
            if not success:
                msg = f"Failed to connect to camera room for {camera_name}"
                raise Exception(msg)
            logger.info(
                f"Connected to camera room for {camera_name}: {room_id} in workspace {self.workspace_id}"
            )

        # Connect to joint input room as consumer
        success = await self.joint_input_consumer.connect(
            self.workspace_id,
            self.joint_input_room_id,
            f"{self.session_id}-joint-input-consumer",
        )
        if not success:
            msg = "Failed to connect to joint input room"
            raise Exception(msg)

        # Connect to joint output room as producer
        success = await self.joint_output_producer.connect(
            self.workspace_id,
            self.joint_output_room_id,
            f"{self.session_id}-joint-output-producer",
        )
        if not success:
            msg = "Failed to connect to joint output room"
            raise Exception(msg)

        logger.info(
            f"Connected to all rooms for session {self.session_id} in workspace {self.workspace_id}"
        )

    async def start_inference(self):
        """Start the inference loop."""
        if self.status != "ready":
            msg = f"Session not ready. Current status: {self.status}"
            raise Exception(msg)

        self.status = "running"
        self.inference_task = asyncio.create_task(self._inference_loop())
        logger.info(f"Started inference for session {self.session_id}")

    async def stop_inference(self):
        """Stop the inference loop."""
        if self.inference_task:
            self.inference_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.inference_task
            self.inference_task = None

        self.status = "stopped"
        logger.info(f"Stopped inference for session {self.session_id}")

    async def restart_inference(self):
        """Restart the inference loop (stop if running, then start)."""
        logger.info(f"Restarting inference for session {self.session_id}")

        # Stop current inference if running
        await self.stop_inference()

        # Reset internal state for fresh start
        self._reset_session_state()

        # Start inference again
        await self.start_inference()

        logger.info(f"Successfully restarted inference for session {self.session_id}")

    def _reset_session_state(self):
        """Reset session state for restart."""
        # Clear action queue
        self.action_queue.clear()

        # Reset complete joint state to zeros
        self.complete_joint_state.fill(0.0)

        # Reset image update flags
        for camera_name in self.camera_names:
            self.images_updated[camera_name] = False
        self.joints_updated = False

        # Reset timing
        self.last_queue_cleanup = time.time()

        # Reset inference engine state if available
        if self.inference_engine:
            self.inference_engine.reset()

        # Reset some statistics (but keep cumulative counts)
        self.stats["actions_in_queue"] = 0

        logger.info(f"Reset session state for {self.session_id}")

    async def _timeout_monitor(self):
        """Monitor session for inactivity timeout."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                current_time = time.time()
                inactive_time = current_time - self.last_activity_time

                if inactive_time > self.timeout_seconds:
                    logger.warning(
                        f"Session {self.session_id} has been inactive for "
                        f"{inactive_time:.1f} seconds (timeout: {self.timeout_seconds}s). "
                        f"Marking for cleanup."
                    )
                    self.status = "timeout"
                    # Don't cleanup here - let the session manager handle it
                    break
                if inactive_time > self.timeout_seconds * 0.8:  # Warn at 80% of timeout
                    logger.info(
                        f"Session {self.session_id} inactive for {inactive_time:.1f}s, "
                        f"will timeout in {self.timeout_seconds - inactive_time:.1f}s"
                    )

            except asyncio.CancelledError:
                logger.info(f"Timeout monitor cancelled for session {self.session_id}")
                break
            except Exception as e:
                logger.exception(
                    f"Error in timeout monitor for session {self.session_id}: {e}"
                )
                break

    def _all_cameras_have_data(self) -> bool:
        """Check if we have received data from all cameras."""
        return all(
            camera_name in self.latest_images for camera_name in self.camera_names
        )

    async def _inference_loop(self):
        """Main inference loop that processes incoming data and sends commands."""
        logger.info(f"Starting inference loop for session {self.session_id}")
        logger.info(
            f"Control frequency: {self.control_frequency_hz} Hz, Inference frequency: {self.inference_frequency_hz} Hz"
        )
        logger.info(
            f"Waiting for data from {len(self.camera_names)} cameras: {self.camera_names}"
        )

        inference_counter = 0
        target_dt = 1.0 / self.control_frequency_hz  # Control loop period
        inference_interval = (
            self.control_frequency_hz // self.inference_frequency_hz
        )  # How many control steps per inference

        while True:
            loop_start_time = asyncio.get_event_loop().time()

            # Check if we have images from all cameras and joint data
            if (
                self._all_cameras_have_data()
                and self.latest_joint_positions is not None
            ):
                # Removed verbose data logging
                # Only run inference at the specified frequency and when queue is empty
                should_run_inference = len(self.action_queue) == 0 or (
                    inference_counter % inference_interval == 0
                    and len(self.action_queue) < 3
                )

                if should_run_inference:
                    # Only log inference runs occasionally to reduce overhead
                    if self.stats["inference_count"] % 10 == 0:
                        logger.info(
                            f"Running inference #{self.stats['inference_count']} for session {self.session_id} "
                            f"(queue length: {len(self.action_queue)})"
                        )

                    try:
                        # Verify joint positions have correct shape before inference
                        if self.latest_joint_positions.shape != (6,):
                            logger.error(
                                f"Invalid joint positions shape: {self.latest_joint_positions.shape}, "
                                f"expected (6,). Values: {self.latest_joint_positions}"
                            )
                            # Fix the shape by resetting to complete joint state
                            self.latest_joint_positions = (
                                self.complete_joint_state.copy()
                            )

                        logger.debug(
                            f"Running inference with joint positions shape: {self.latest_joint_positions.shape}, "
                            f"values: {self.latest_joint_positions}"
                        )

                        # Prepare inference arguments
                        inference_kwargs = {
                            "images": self.latest_images,
                            "joint_positions": self.latest_joint_positions,
                        }

                        # Add language instruction for vision-language policies
                        if (
                            self.policy_type in {"pi0", "pi0fast", "smolvla"}
                            and self.language_instruction
                        ):
                            inference_kwargs["task"] = self.language_instruction

                        # Run inference to get action chunk
                        predicted_actions = await self.inference_engine.predict(
                            **inference_kwargs
                        )

                        # ACT returns a chunk of actions, we need to queue them
                        if len(predicted_actions.shape) == 1:
                            # Single action returned, use it directly
                            actions_to_queue = [predicted_actions]
                        else:
                            # Multiple actions in chunk, take first n_action_steps
                            actions_to_queue = predicted_actions[: self.n_action_steps]

                        # Add actions to queue
                        for action in actions_to_queue:
                            joint_commands = (
                                self.inference_engine.get_joint_commands_with_names(
                                    action
                                )
                            )
                            self.action_queue.append(joint_commands)

                        self.stats["inference_count"] += 1
                        # Reset image update flags
                        for camera_name in self.camera_names:
                            self.images_updated[camera_name] = False
                        self.joints_updated = False
                        logger.debug(
                            f"Added {len(actions_to_queue)} actions to queue for session {self.session_id}"
                        )

                    except Exception as e:
                        logger.exception(
                            f"Inference failed for session {self.session_id}: {e}"
                        )
                        self.stats["errors"] += 1

                # Send action from queue if available
                if len(self.action_queue) > 0:
                    joint_commands = self.action_queue.popleft()
                    try:
                        # Only log commands occasionally
                        if self.stats["commands_sent"] % 100 == 0:
                            logger.info(
                                f"🤖 Sent {self.stats['commands_sent']} commands. Latest: {joint_commands[0]['name']}={joint_commands[0]['value']:.1f}"
                            )

                        await self.joint_output_producer.send_joint_update(
                            joint_commands
                        )
                        self.stats["commands_sent"] += 1
                        self.stats["actions_in_queue"] = len(self.action_queue)

                        # Store command values for responsiveness check
                        command_values = np.array(
                            [cmd["value"] for cmd in joint_commands], dtype=np.float32
                        )
                        self.last_command_values = command_values
                    except Exception as e:
                        logger.exception(
                            f"Failed to send joint commands for session {self.session_id}: {e}"
                        )
                        self.stats["errors"] += 1
                # Log when queue is empty occasionally
                elif inference_counter % 100 == 0:
                    logger.debug(
                        f"No actions in queue to send (inference #{inference_counter})"
                    )

            # Periodic memory cleanup
            current_time = asyncio.get_event_loop().time()
            if current_time - self.last_queue_cleanup > self.queue_cleanup_interval:
                # Clear stale actions if queue is getting full
                if len(self.action_queue) > 80:  # 80% of maxlen
                    logger.debug(
                        f"Clearing stale actions from queue for session {self.session_id}"
                    )
                    self.action_queue.clear()
                self.last_queue_cleanup = current_time

            inference_counter += 1

            # Precise timing control for consistent control frequency
            elapsed_time = asyncio.get_event_loop().time() - loop_start_time
            sleep_time = target_dt - elapsed_time

            if sleep_time > 0.001:  # Use asyncio.sleep for longer waits
                await asyncio.sleep(sleep_time)
            elif sleep_time > 0:  # Use busy_wait for precise short delays
                busy_wait(sleep_time)
            elif sleep_time < -0.01:  # Log if we're running significantly slow
                logger.warning(
                    f"Control loop running slow for session {self.session_id}: {elapsed_time * 1000:.1f}ms (target: {target_dt * 1000:.1f}ms)"
                )

    async def cleanup(self):
        """Clean up session resources."""
        logger.info(f"Cleaning up session {self.session_id}")

        # Stop timeout monitoring
        if self.timeout_check_task:
            self.timeout_check_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.timeout_check_task
            self.timeout_check_task = None

        # Stop inference
        await self.stop_inference()

        # Disconnect Arena clients
        for camera_name, consumer in self.camera_consumers.items():
            await consumer.stop_receiving()
            await consumer.disconnect()
            logger.info(f"Disconnected camera consumer for {camera_name}")

        if self.joint_input_consumer:
            await self.joint_input_consumer.disconnect()
        if self.joint_output_producer:
            await self.joint_output_producer.disconnect()

        # Clean up inference engine
        if self.inference_engine:
            del self.inference_engine
            self.inference_engine = None

        logger.info(f"Session {self.session_id} cleanup completed")

    def get_status(self) -> dict:
        """Get current session status."""
        status_dict = {
            "session_id": self.session_id,
            "status": self.status,
            "policy_path": self.policy_path,
            "policy_type": self.policy_type,
            "camera_names": self.camera_names,
            "workspace_id": self.workspace_id,
            "rooms": {
                "workspace_id": self.workspace_id,
                "camera_room_ids": self.camera_room_ids,
                "joint_input_room_id": self.joint_input_room_id,
                "joint_output_room_id": self.joint_output_room_id,
            },
            "stats": self.stats.copy(),
            "error_message": self.error_message,
            "joint_state": {
                "complete_joint_state": self.complete_joint_state.tolist(),
                "latest_joint_positions": (
                    self.latest_joint_positions.tolist()
                    if self.latest_joint_positions is not None
                    else None
                ),
                "joint_state_shape": (
                    self.latest_joint_positions.shape
                    if self.latest_joint_positions is not None
                    else None
                ),
            },
        }

        # Add inference engine stats if available
        if self.inference_engine:
            status_dict["inference_stats"] = self.inference_engine.get_model_info()

        return status_dict


class SessionManager:
    """Manages multiple inference sessions and their lifecycle."""

    def __init__(self):
        self.sessions: dict[str, InferenceSession] = {}
        self.cleanup_task: asyncio.Task | None = None
        self._start_cleanup_task()

    def _start_cleanup_task(self):
        """Start the automatic cleanup task for timed-out sessions."""
        try:
            # Only start if we're in an async context
            loop = asyncio.get_running_loop()
            self.cleanup_task = loop.create_task(self._periodic_cleanup())
        except RuntimeError:
            # No event loop running yet, will start later
            pass

    async def _periodic_cleanup(self):
        """Periodically check for and clean up timed-out sessions."""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                # Find sessions that have timed out
                timed_out_sessions = []
                for session_id, session in self.sessions.items():
                    if session.status == "timeout":
                        timed_out_sessions.append(session_id)

                # Clean up timed-out sessions
                for session_id in timed_out_sessions:
                    logger.info(f"Auto-cleaning up timed-out session: {session_id}")
                    await self.delete_session(session_id)

            except asyncio.CancelledError:
                logger.info("Periodic cleanup task cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in periodic cleanup: {e}")
                # Continue running even if there's an error

    async def create_session(
        self,
        session_id: str,
        policy_path: str,
        camera_names: list[str] | None = None,
        arena_server_url: str = "http://localhost:8000",
        workspace_id: str | None = None,
        policy_type: str = "act",
        language_instruction: str | None = None,
    ) -> dict[str, str]:
        """Create a new inference session."""
        if camera_names is None:
            camera_names = ["front"]
        if session_id in self.sessions:
            msg = f"Session {session_id} already exists"
            raise ValueError(msg)

        # Create camera rooms using VideoProducer
        video_temp_client = VideoProducer(arena_server_url)
        camera_room_ids = {}

        # Use provided workspace_id or create new one
        if workspace_id:
            target_workspace_id = workspace_id
            logger.info(
                f"Using provided workspace ID {target_workspace_id} for session {session_id}"
            )

            # Create all camera rooms in the specified workspace
            for camera_name in camera_names:
                _, room_id = await video_temp_client.create_room(
                    workspace_id=target_workspace_id,
                    room_id=f"{session_id}-{camera_name}",
                )
                camera_room_ids[camera_name] = room_id
        else:
            # Create first camera room to get new workspace_id
            first_camera = camera_names[0]
            target_workspace_id, first_room_id = await video_temp_client.create_room(
                room_id=f"{session_id}-{first_camera}"
            )
            logger.info(
                f"Generated new workspace ID {target_workspace_id} for session {session_id}"
            )

            # Store the first room
            camera_room_ids[first_camera] = first_room_id

            # Create remaining camera rooms in the same workspace
            for camera_name in camera_names[1:]:
                _, room_id = await video_temp_client.create_room(
                    workspace_id=target_workspace_id,
                    room_id=f"{session_id}-{camera_name}",
                )
                camera_room_ids[camera_name] = room_id

        # Create joint rooms using RoboticsProducer in the same workspace
        robotics_temp_client = RoboticsProducer(arena_server_url)
        _, joint_input_room_id = await robotics_temp_client.create_room(
            workspace_id=target_workspace_id, room_id=f"{session_id}-joint-input"
        )
        _, joint_output_room_id = await robotics_temp_client.create_room(
            workspace_id=target_workspace_id, room_id=f"{session_id}-joint-output"
        )

        logger.info(
            f"Created rooms for session {session_id} in workspace {target_workspace_id}:"
        )
        for camera_name, room_id in camera_room_ids.items():
            logger.info(f"  Camera room ({camera_name}): {room_id}")
        logger.info(f"  Joint input room: {joint_input_room_id}")
        logger.info(f"  Joint output room: {joint_output_room_id}")

        # Create session
        session = InferenceSession(
            session_id=session_id,
            policy_path=policy_path,
            camera_names=camera_names,
            arena_server_url=arena_server_url,
            workspace_id=target_workspace_id,
            camera_room_ids=camera_room_ids,
            joint_input_room_id=joint_input_room_id,
            joint_output_room_id=joint_output_room_id,
            policy_type=policy_type,
            language_instruction=language_instruction,
        )

        # Initialize session
        await session.initialize()

        # Store session
        self.sessions[session_id] = session

        # Start cleanup task if not already running
        if not self.cleanup_task or self.cleanup_task.done():
            self._start_cleanup_task()

        return {
            "workspace_id": target_workspace_id,
            "camera_room_ids": camera_room_ids,
            "joint_input_room_id": joint_input_room_id,
            "joint_output_room_id": joint_output_room_id,
        }

    async def get_session_status(self, session_id: str) -> dict:
        """Get status of a specific session."""
        if session_id not in self.sessions:
            msg = f"Session {session_id} not found"
            raise KeyError(msg)
        return self.sessions[session_id].get_status()

    async def start_inference(self, session_id: str):
        """Start inference for a specific session."""
        if session_id not in self.sessions:
            msg = f"Session {session_id} not found"
            raise KeyError(msg)
        await self.sessions[session_id].start_inference()

    async def stop_inference(self, session_id: str):
        """Stop inference for a specific session."""
        if session_id not in self.sessions:
            msg = f"Session {session_id} not found"
            raise KeyError(msg)
        await self.sessions[session_id].stop_inference()

    async def restart_inference(self, session_id: str):
        """Restart inference for a specific session."""
        if session_id not in self.sessions:
            msg = f"Session {session_id} not found"
            raise KeyError(msg)
        await self.sessions[session_id].restart_inference()

    async def delete_session(self, session_id: str):
        """Delete a session and clean up all resources."""
        if session_id not in self.sessions:
            msg = f"Session {session_id} not found"
            raise KeyError(msg)

        session = self.sessions[session_id]
        await session.cleanup()
        del self.sessions[session_id]
        logger.info(f"Deleted session {session_id}")

    async def list_sessions(self) -> list[dict]:
        """List all sessions with their status."""
        return [session.get_status() for session in self.sessions.values()]

    async def cleanup_all_sessions(self):
        """Clean up all sessions."""
        logger.info("Cleaning up all sessions...")

        # Stop the cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.cleanup_task
            self.cleanup_task = None

        # Clean up all sessions
        for session_id in list(self.sessions.keys()):
            await self.delete_session(session_id)
        logger.info("All sessions cleaned up")
