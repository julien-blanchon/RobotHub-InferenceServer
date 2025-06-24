# 🤖 Integrated Inference Server

This is an integrated ACT Model Inference Server that combines **FastAPI** and **Gradio** on a single port, perfect for deployment and development.

## 🚀 Quick Start

```bash
# Install dependencies
uv sync

# Run the integrated server
uv run python launch_simple.py --host 0.0.0.0 --port 7860
```

## 📡 Access Points

Once running, you can access:

- **🎨 Gradio UI**: http://localhost:7860/
- **📖 API Documentation**: http://localhost:7860/api/docs  
- **🔄 Health Check**: http://localhost:7860/api/health
- **📋 OpenAPI Schema**: http://localhost:7860/api/openapi.json

## 🏗️ Architecture

### Integration Approach
- **Single Process**: Everything runs in one Python process
- **Single Port**: Both API and UI on the same port (7860)
- **FastAPI at `/api`**: Full REST API with automatic documentation
- **Gradio at `/`**: User-friendly web interface
- **Direct Session Management**: UI communicates directly with session manager (no HTTP overhead)

### Key Components

1. **`simple_integrated.py`**: Main integration logic
   - Creates FastAPI app and mounts it at `/api`
   - Creates Gradio interface and mounts it at `/`
   - Provides `SimpleServerManager` for direct session access

2. **`launch_simple.py`**: Entry point script
   - Handles command-line arguments
   - Starts the integrated application

3. **`main.py`**: Core FastAPI application
   - Session management endpoints
   - Policy loading and inference
   - OpenAPI documentation

## 🔧 Features

### For UI Users
- ✅ **Simple Interface**: Create and manage AI sessions through web UI
- ✅ **Real-time Status**: Live session monitoring and control
- ✅ **Direct Performance**: No HTTP overhead for UI operations

### For API Users  
- ✅ **Full REST API**: Complete programmatic access
- ✅ **Interactive Docs**: Automatic Swagger/OpenAPI documentation
- ✅ **Standard Endpoints**: `/sessions`, `/health`, etc.
- ✅ **CORS Enabled**: Ready for frontend integration

### For Deployment
- ✅ **Single Port**: Easy to deploy behind reverse proxy
- ✅ **Docker Ready**: Dockerfile included
- ✅ **Health Checks**: Built-in monitoring endpoints
- ✅ **HuggingFace Spaces**: Perfect for cloud deployment

## 📋 API Usage Examples

### Health Check
```bash
curl http://localhost:7860/api/health
```

### Create Session
```bash
curl -X POST http://localhost:7860/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my-robot",
    "policy_path": "./checkpoints/act_so101_beyond",
    "camera_names": ["front"],
    "arena_server_url": "http://localhost:8000"
  }'
```

### Start Inference
```bash
curl -X POST http://localhost:7860/api/sessions/my-robot/start
```

### Get Session Status
```bash
curl http://localhost:7860/api/sessions/my-robot
```

## 🐳 Docker Usage

```bash
# Build
docker build -t inference-server .

# Run
docker run -p 7860:7860 inference-server
```

## 🔍 Testing

Run the integration test to verify everything works:

```bash
uv run python test_integration.py
```

## 💡 Development Tips

### Use Both Interfaces
- **Development**: Use Gradio UI for quick testing and setup
- **Production**: Use REST API for automated systems
- **Integration**: Both can run simultaneously

### Session Management
- UI uses direct session manager access (faster)
- API uses HTTP endpoints (standard REST)
- Both share the same underlying session data

### Debugging
- Check logs for startup issues
- Use `/api/health` to verify API is working
- Visit `/api/docs` for interactive API testing

## 🚀 Benefits of This Approach

1. **Flexibility**: Use UI or API as needed
2. **Performance**: Direct access for UI, standard REST for API
3. **Deployment**: Single port, single process
4. **Documentation**: Auto-generated API docs
5. **Development**: Fast iteration with integrated setup 