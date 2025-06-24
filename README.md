---
title: LeRobot Arena - AI Inference Server
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
suggested_hardware: t4-small
suggested_storage: medium
short_description: Real-time ACT model inference server for robot control
tags:
  - robotics
  - ai
  - inference
  - control
  - act-model
  - transformer
  - real-time
  - gradio
  - fastapi
  - computer-vision
pinned: false
fullWidth: true
---

# Inference Server

🤖 **Real-time ACT Model Inference Server for Robot Control**

This server provides ACT (Action Chunking Transformer) model inference for robotics applications using the transport server communication system. It includes a user-friendly Gradio web interface for easy setup and management.

## ✨ Features

- **Real-time AI Inference**: Run ACT models for robot control at 20Hz control frequency
- **Multi-Camera Support**: Handle multiple camera streams with different names
- **Web Interface**: User-friendly Gradio UI for setup and monitoring
- **Session Management**: Create, start, stop, and monitor inference sessions
- **Automatic Timeout**: Sessions automatically cleanup after 10 minutes of inactivity
- **Debug Tools**: Built-in debugging and monitoring endpoints
- **Flexible Configuration**: Support for custom model paths, camera configurations
- **No External Dependencies**: Direct Python execution without subprocess calls

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- UV package manager (recommended)
- Trained ACT model
- Transport server running

### 1. Installation

```bash
cd backend/ai-server

# Install dependencies using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Launch the Application

#### **🚀 Simple Integrated Mode (Recommended)**
```bash
# Everything runs in one process - no subprocess issues!
python launch_simple.py

# Or using the CLI
python -m inference_server.cli --simple
```

This will:
- Run everything on `http://localhost:7860`
- Direct session management (no HTTP API calls)
- No external subprocess dependencies
- Most robust and simple deployment!

#### **🔧 Development Mode (Separate Processes)**
```bash
# Traditional approach with separate server and UI
python -m inference_server.cli
```

This will:
- Start the AI server on `http://localhost:8001`
- Launch the Gradio UI on `http://localhost:7860`
- Better for development and debugging

### 3. Using the Web Interface

1. **Check Server Status**: The interface will automatically check if the AI server is running
2. **Configure Your Robot**: Enter your model path and camera setup
3. **Create & Start Session**: Click the button to set up AI control
4. **Monitor Performance**: Use the status panel to monitor inference

## 🎯 Workflow Guide

### Step 1: AI Server
- The server status will be displayed at the top
- Click "Start Server" if it's not already running
- Use "Check Status" to verify connectivity

### Step 2: Set Up Robot AI
- **Session Name**: Give your session a unique name (e.g., "my-robot-01")
- **AI Model Path**: Path to your trained ACT model (e.g., "./checkpoints/act_so101_beyond")
- **Camera Names**: Comma-separated list of camera names (e.g., "front,wrist,overhead")
- Click "Create & Start AI Control" to begin

### Step 3: Control Session
- The session ID will be auto-filled after creation
- Use Start/Stop buttons to control inference
- Click "Status" to see detailed performance metrics

## 🛠️ Advanced Usage

### CLI Options

```bash
# Simple integrated mode (recommended)
python -m inference_server.cli --simple

# Development mode (separate processes)
python -m inference_server.cli

# Launch only the server
python -m inference_server.cli --server-only

# Launch only the UI (server must be running separately)  
python -m inference_server.cli --ui-only

# Custom ports
python -m inference_server.cli --server-port 8002 --ui-port 7861

# Enable public sharing
python -m inference_server.cli --share

# For deployment (recommended)
python -m inference_server.cli --simple --host 0.0.0.0 --share
```

### API Endpoints

The server provides a REST API for programmatic access:

- `GET /health` - Server health check
- `POST /sessions` - Create new session
- `GET /sessions` - List all sessions
- `GET /sessions/{id}` - Get session details
- `POST /sessions/{id}/start` - Start inference
- `POST /sessions/{id}/stop` - Stop inference
- `POST /sessions/{id}/restart` - Restart inference
- `DELETE /sessions/{id}` - Delete session

#### Debug Endpoints
- `GET /debug/system` - System information (CPU, memory, GPU)
- `GET /debug/sessions/{id}/queue` - Action queue details
- `POST /debug/sessions/{id}/reset` - Reset session state

### Configuration

#### Joint Value Convention
- All joint inputs/outputs use **NORMALIZED VALUES**
- Most joints: -100 to +100 (RANGE_M100_100)
- Gripper: 0 to 100 (RANGE_0_100)
- This matches the training data format exactly

#### Camera Support
- Supports arbitrary number of camera streams
- Each camera has a unique name (e.g., "front", "wrist", "overhead")
- All camera streams are synchronized for inference
- Images expected in RGB format, uint8 [0-255]

## 📊 Monitoring

### Session Status Indicators
- 🟢 **Running**: Inference active and processing
- 🟡 **Ready**: Session created but inference not started
- 🔴 **Stopped**: Inference stopped
- 🟠 **Initializing**: Session being set up

### Smart Session Control
The UI now provides intelligent feedback:
- ℹ️ **Already Running**: When trying to start a running session
- ℹ️ **Already Stopped**: When trying to stop a stopped session
- 💡 **Smart Suggestions**: Context-aware tips based on current status

### Performance Metrics
- **Inferences**: Total number of model inferences performed
- **Commands Sent**: Joint commands sent to robot
- **Queue Length**: Actions waiting in the queue
- **Errors**: Number of errors encountered
- **Data Flow**: Images and joint states received

## 🐳 Docker Usage

### Build the Image
```bash
cd services/inference-server
docker build -t inference-server .
```

### Run the Container
```bash
# Basic usage
docker run -p 7860:7860 inference-server

# With environment variables
docker run -p 7860:7860 \
  -e DEFAULT_ARENA_SERVER_URL=http://your-server.com \
  -e DEFAULT_MODEL_PATH=./checkpoints/your-model \
  inference-server

# With GPU support
docker run --gpus all -p 7860:7860 inference-server
```

## 🔧 Troubleshooting



### Common Issues

1. **Server Won't Start**
   - Check if port 8001 is available
   - Verify model path exists and is accessible
   - Check dependencies are installed correctly

2. **Session Creation Fails**
   - Verify model path is correct
   - Check Arena server is running on specified URL
   - Ensure camera names match your robot configuration

3. **Poor Performance**
   - Monitor system resources in the debug panel
   - Check if GPU is being used for inference
   - Verify control/inference frequency settings

4. **Connection Issues**
   - Verify Arena server URL is correct
   - Check network connectivity
   - Ensure workspace/room IDs are valid

### Debug Mode

Enable debug mode for detailed logging:

```bash
uv run python -m lerobot_arena_ai_server.cli --debug
```

### System Requirements

- **CPU**: Multi-core recommended for 30Hz control
- **Memory**: 8GB+ RAM recommended
- **GPU**: CUDA-compatible GPU for fast inference (optional but recommended)
- **Network**: Stable connection to Arena server

## 📚 Architecture

### Integrated Mode (Recommended)
```
┌─────────────────────────────────────┐    ┌─────────────────┐
│        Single Application           │    │  LeRobot Arena  │
│  ┌─────────────┐  ┌─────────────┐   │◄──►│   (Port 8000)   │
│  │ Gradio UI   │  │ AI Server   │   │    └─────────────────┘
│  │    (/)      │  │  (/api/*)   │   │             │
│  └─────────────┘  └─────────────┘   │             │
│       (Port 7860)                   │        Robot/Cameras
└─────────────────────────────────────┘
           │
      Web Browser
```

### Development Mode
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gradio UI     │    │   AI Server     │    │  LeRobot Arena  │
│   (Port 7860)   │◄──►│   (Port 8001)   │◄──►│   (Port 8000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    Web Browser              ACT Model              Robot/Cameras
                             Inference
```

### Data Flow

1. **Camera Data**: Robot cameras → Arena → AI Server
2. **Joint State**: Robot joints → Arena → AI Server  
3. **AI Inference**: Images + Joint State → ACT Model → Actions
4. **Control Commands**: Actions → Arena → Robot

### Session Lifecycle

1. **Create**: Set up rooms in Arena, load ACT model
2. **Start**: Begin inference loop (3Hz) and control loop (30Hz)
3. **Running**: Process camera/joint data, generate actions
4. **Stop**: Pause inference, maintain connections
5. **Delete**: Clean up resources, disconnect from Arena

## 🤝 Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Submit pull requests

## 📄 License

This project follows the same license as the parent LeRobot Arena project.

---

For more information, see the [LeRobot Arena documentation](../../README.md).
