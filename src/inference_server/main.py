import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
    logger.info("🚀 RobotHub Inference Server starting up...")
    yield
    logger.info("🔄 RobotHub Inference Server shutting down...")
    await session_manager.cleanup_all_sessions()
    logger.info("✅ RobotHub Inference Server shutdown complete")


# FastAPI app
app = FastAPI(
    title="RobotHub Inference Server",
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
    transport_server_url: str
    camera_names: list[str] = ["front"]  # Support multiple cameras
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
    camera_names: list[str]
    workspace_id: str
    rooms: dict
    stats: dict
    inference_stats: dict | None = None
    error_message: str | None = None


# Health check endpoints
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {"message": "RobotHub Inference Server is running", "status": "healthy"}


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "active_sessions": len(session_manager.sessions),
        "session_ids": list(session_manager.sessions.keys()),
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
            transport_server_url=request.transport_server_url,
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


# Session control endpoints
@app.post("/sessions/{session_id}/start", tags=["Control"])
async def start_inference(session_id: str):
    """Start inference for a session."""
    try:
        await session_manager.start_inference(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    except Exception as e:
        logger.exception(f"Failed to start inference for session {session_id}")
        raise HTTPException(status_code=500, detail=f"Failed to start inference: {e!s}")
    else:
        return {"message": f"Inference started for session {session_id}"}


@app.post("/sessions/{session_id}/stop", tags=["Control"])
async def stop_inference(session_id: str):
    """Stop inference for a session."""
    try:
        await session_manager.stop_inference(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    else:
        return {"message": f"Inference started for session {session_id}"}


@app.post("/sessions/{session_id}/restart", tags=["Control"])
async def restart_inference(session_id: str):
    """Restart inference for a session."""
    try:
        await session_manager.restart_inference(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    except Exception as e:
        logger.exception(f"Failed to restart inference for session {session_id}")
        raise HTTPException(
            status_code=500, detail=f"Failed to restart inference: {e!s}"
        )
    else:
        return {"message": f"Inference restarted for session {session_id}"}


@app.delete("/sessions/{session_id}", tags=["Sessions"])
async def delete_session(session_id: str):
    """Delete a session."""
    try:
        await session_manager.delete_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    else:
        return {"message": f"Session {session_id} deleted"}


# Main entry point
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8001"))
    uvicorn.run(
        "inference_server.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
    )
