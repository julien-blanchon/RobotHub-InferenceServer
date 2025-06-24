import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from inference_server.models import list_supported_policies
from inference_server.session_manager import SessionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global session manager
session_manager = SessionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle app startup and shutdown."""
    logger.info("🚀 Inference Server starting up...")
    yield
    logger.info("🔄 Inference Server shutting down...")
    await session_manager.cleanup_all_sessions()
    logger.info("✅ Inference Server shutdown complete")


# FastAPI app
app = FastAPI(
    title="Inference Server",
    description="Multi-Policy Model Inference Server for Real-time Robot Control",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class CreateSessionRequest(BaseModel):
    session_id: str
    policy_path: str
    camera_names: list[str] = ["front"]  # Support multiple cameras
    arena_server_url: str = "http://localhost:8000"
    workspace_id: str | None = None  # Optional workspace ID
    policy_type: str = "act"  # Policy type: act, pi0, pi0fast, smolvla, diffusion
    language_instruction: str | None = None  # For vision-language policies


class CreateSessionResponse(BaseModel):
    workspace_id: str
    camera_room_ids: dict[str, str]  # {camera_name: room_id}
    joint_input_room_id: str
    joint_output_room_id: str


class SessionStatusResponse(BaseModel):
    session_id: str
    status: str
    policy_path: str
    policy_type: str
    camera_names: list[str]  # Multiple camera names
    workspace_id: str
    rooms: dict
    stats: dict
    inference_stats: dict | None = None
    error_message: str | None = None


# Health check
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {"message": "Inference Server is running", "status": "healthy"}


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "active_sessions": len(session_manager.sessions),
        "session_ids": list(session_manager.sessions.keys()),
    }


@app.get("/policies", tags=["Policies"])
async def list_policies():
    """List supported policy types."""
    return {
        "supported_policies": list_supported_policies(),
        "description": "Available policy types for inference",
    }


# Session management endpoints
@app.post("/sessions", response_model=CreateSessionResponse, tags=["Sessions"])
async def create_session(request: CreateSessionRequest):
    """
    Create a new inference session.

    If workspace_id is provided, all rooms will be created in that workspace.
    If workspace_id is not provided, a new workspace will be generated automatically.
    All rooms for a session (cameras + joints) are always created in the same workspace.
    """
    try:
        room_ids = await session_manager.create_session(
            session_id=request.session_id,
            policy_path=request.policy_path,
            camera_names=request.camera_names,
            arena_server_url=request.arena_server_url,
            workspace_id=request.workspace_id,
            policy_type=request.policy_type,
            language_instruction=request.language_instruction,
        )
        return CreateSessionResponse(**room_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to create session {request.session_id}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {e!s}")


@app.get("/sessions", response_model=list[SessionStatusResponse], tags=["Sessions"])
async def list_sessions():
    """List all sessions."""
    sessions = await session_manager.list_sessions()
    return [SessionStatusResponse(**session) for session in sessions]


@app.get(
    "/sessions/{session_id}", response_model=SessionStatusResponse, tags=["Sessions"]
)
async def get_session_status(session_id: str):
    """Get status of a specific session."""
    try:
        status = await session_manager.get_session_status(session_id)
        return SessionStatusResponse(**status)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")


@app.post("/sessions/{session_id}/start", tags=["Control"])
async def start_inference(session_id: str):
    """Start inference for a session."""
    try:
        await session_manager.start_inference(session_id)
        return {"message": f"Inference started for session {session_id}"}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    except Exception as e:
        logger.exception(f"Failed to start inference for session {session_id}")
        raise HTTPException(status_code=500, detail=f"Failed to start inference: {e!s}")


@app.post("/sessions/{session_id}/stop", tags=["Control"])
async def stop_inference(session_id: str):
    """Stop inference for a session."""
    try:
        await session_manager.stop_inference(session_id)
        return {"message": f"Inference stopped for session {session_id}"}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")


@app.post("/sessions/{session_id}/restart", tags=["Control"])
async def restart_inference(session_id: str):
    """Restart inference for a session."""
    try:
        await session_manager.restart_inference(session_id)
        return {"message": f"Inference restarted for session {session_id}"}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    except Exception as e:
        logger.exception(f"Failed to restart inference for session {session_id}")
        raise HTTPException(
            status_code=500, detail=f"Failed to restart inference: {e!s}"
        )


@app.delete("/sessions/{session_id}", tags=["Sessions"])
async def delete_session(session_id: str):
    """Delete a session."""
    try:
        await session_manager.delete_session(session_id)
        return {"message": f"Session {session_id} deleted"}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")


# Debug endpoints for enhanced monitoring
@app.get("/debug/system", tags=["Debug"])
async def get_system_info():
    """Get system information for debugging."""
    import psutil
    import torch

    try:
        # System info
        system_info = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
            },
            "disk": {
                "total": psutil.disk_usage("/").total,
                "used": psutil.disk_usage("/").used,
                "percent": psutil.disk_usage("/").percent,
            },
        }

        # GPU info if available
        if torch.cuda.is_available():
            system_info["gpu"] = {
                "device_count": torch.cuda.device_count(),
                "current_device": torch.cuda.current_device(),
                "device_name": torch.cuda.get_device_name(),
                "memory_allocated": torch.cuda.memory_allocated(),
                "memory_cached": torch.cuda.memory_reserved(),
            }

        return system_info
    except Exception as e:
        return {"error": f"Failed to get system info: {e}"}


@app.get("/debug/logs", tags=["Debug"])
async def get_recent_logs():
    """Get recent log entries for debugging."""
    try:
        # This is a simple implementation - in production you might want to read from actual log files
        return {
            "message": "Log endpoint available",
            "note": "Implement actual log reading if needed",
            "active_sessions": len(session_manager.sessions),
        }
    except Exception as e:
        return {"error": f"Failed to get logs: {e}"}


@app.post("/debug/sessions/{session_id}/reset", tags=["Debug"])
async def debug_reset_session(session_id: str):
    """Reset a session's internal state for debugging."""
    try:
        if session_id not in session_manager.sessions:
            raise HTTPException(
                status_code=404, detail=f"Session {session_id} not found"
            )

        session = session_manager.sessions[session_id]

        # Reset inference engine if available
        if session.inference_engine:
            session.inference_engine.reset()

        # Clear action queue
        session.action_queue.clear()

        # Reset flags
        for camera_name in session.camera_names:
            session.images_updated[camera_name] = False
        session.joints_updated = False

        return {"message": f"Session {session_id} state reset successfully"}

    except Exception as e:
        logger.exception(f"Failed to reset session {session_id}")
        raise HTTPException(status_code=500, detail=f"Failed to reset session: {e}")


@app.get("/debug/sessions/{session_id}/queue", tags=["Debug"])
async def get_session_queue_info(session_id: str):
    """Get detailed information about a session's action queue."""
    try:
        if session_id not in session_manager.sessions:
            raise HTTPException(
                status_code=404, detail=f"Session {session_id} not found"
            )

        session = session_manager.sessions[session_id]

        return {
            "session_id": session_id,
            "queue_length": len(session.action_queue),
            "queue_maxlen": session.action_queue.maxlen,
            "n_action_steps": session.n_action_steps,
            "control_frequency_hz": session.control_frequency_hz,
            "inference_frequency_hz": session.inference_frequency_hz,
            "last_queue_cleanup": session.last_queue_cleanup,
            "data_status": {
                "has_joint_data": session.latest_joint_positions is not None,
                "images_status": {
                    camera: camera in session.latest_images
                    for camera in session.camera_names
                },
                "images_updated": session.images_updated.copy(),
                "joints_updated": session.joints_updated,
            },
        }

    except Exception as e:
        logger.exception(f"Failed to get queue info for session {session_id}")
        raise HTTPException(status_code=500, detail=f"Failed to get queue info: {e}")


# Main entry point
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(
        "inference_server.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
    )
