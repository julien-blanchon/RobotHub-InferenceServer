try:
    from .export_openapi import export_openapi_schema
except ImportError:
    export_openapi_schema = None

try:
    from .main import app
except ImportError:
    app = None

from .session_manager import InferenceSession, SessionManager

try:
    from .ui import launch_ui
except ImportError:
    launch_ui = None

__version__ = "0.1.0"
__all__ = [
    "InferenceSession",
    "SessionManager",
]

# Add optional exports if available
if app is not None:
    __all__.append("app")
if export_openapi_schema is not None:
    __all__.append("export_openapi_schema")
if launch_ui is not None:
    __all__.append("launch_ui")
