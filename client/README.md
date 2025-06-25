# RobotHub Inference Server TypeScript Client

A TypeScript client for the RobotHub Inference Server, providing ACT (Action Chunking Transformer) model inference and session management capabilities.

## Features

- ✅ **Fully Generated**: Client is 100% generated from OpenAPI spec
- 🔒 **Type Safe**: Complete TypeScript support with generated types
- 🚀 **Modern**: Built with Bun and modern JavaScript features
- 📦 **Lightweight**: Minimal dependencies, uses fetch API
- 🛠️ **Developer Friendly**: Comprehensive examples and documentation

## Installation

```bash
# Install dependencies
bun install

# Generate client from OpenAPI spec
bun run generate

# Build the client
bun run build
```

## Quick Start

```typescript
import { RobotHubInferenceClient, CreateSessionRequest } from '@robothub/inference-server-client';

// Create client
const client = new RobotHubInferenceClient('http://localhost:8001');

// Check server health
const isHealthy = await client.isHealthy();
if (!isHealthy) {
  console.error('Server is not available');
  process.exit(1);
}

// Create and start a session
const sessionRequest: CreateSessionRequest = {
  session_id: 'my-robot-session',
  policy_path: 'LaetusH/act_so101_beyond',
  camera_names: ['front', 'wrist'],
  transport_server_url: 'http://localhost:8000'
};

const session = await client.createSession(sessionRequest);
await client.startInference('my-robot-session');

// Monitor session
const status = await client.getSessionStatus('my-robot-session');
console.log(`Status: ${status.status}`);

// Clean up
await client.deleteSession('my-robot-session');
```

## API Reference

### Client Creation

```typescript
const client = new RobotHubInferenceClient(baseUrl: string);
```

### Health Check Methods

- `isHealthy()`: Quick boolean health check
- `getHealth()`: Detailed health information

### Session Management

- `createSession(request: CreateSessionRequest)`: Create inference session
- `listSessions()`: List all active sessions
- `getSessionStatus(sessionId: string)`: Get session details
- `deleteSession(sessionId: string)`: Delete session and cleanup

### Inference Control

- `startInference(sessionId: string)`: Start model inference
- `stopInference(sessionId: string)`: Stop model inference  
- `restartInference(sessionId: string)`: Restart model inference

### Utility Methods

- `waitForSessionStatus(sessionId, targetStatus, timeout)`: Wait for status change
- `createAndStartSession(request)`: Create session and start inference in one call

### Debug Methods

- `getSystemInfo()`: Get server system information
- `debugResetSession(sessionId: string)`: Reset session state
- `getSessionQueueInfo(sessionId: string)`: Get action queue details

## Generated Types

All types are generated from the OpenAPI specification:

```typescript
import type { 
  CreateSessionRequest,
  CreateSessionResponse,
  SessionStatusResponse,
  // ... all other types
} from '@robothub/inference-server-client';
```

Key types:
- `CreateSessionRequest`: Session creation parameters
- `CreateSessionResponse`: Session creation result with room IDs
- `SessionStatusResponse`: Complete session status and statistics

## Examples

### Basic Usage
```bash
bun run examples/basic-usage.ts
```

### Quick Example  
```bash
bun run examples/basic-usage.ts --quick
```

## Development

### Scripts

- `bun run generate`: Export OpenAPI schema and generate client
- `bun run build`: Build the client distribution
- `bun run typecheck`: Run TypeScript type checking
- `bun run test`: Run tests
- `bun run clean`: Clean generated files and dist

### Regenerating Client

The client is automatically regenerated when you run `bun run build`. To manually regenerate:

```bash
# Export latest OpenAPI schema from inference server
bun run export-openapi

# Generate TypeScript client from schema
bun run generate-client
```

### File Structure

```
client/
├── src/
│   ├── generated/          # Auto-generated from OpenAPI
│   │   ├── index.ts        # Generated exports
│   │   ├── services.gen.ts # Generated API methods
│   │   ├── types.gen.ts    # Generated TypeScript types
│   │   └── schemas.gen.ts  # Generated schemas
│   └── index.ts            # Main client wrapper
├── examples/
│   └── basic-usage.ts      # Usage examples
├── dist/                   # Built files
├── openapi.json           # Latest OpenAPI schema
└── package.json
```

## Requirements

- **Bun** >= 1.0.0 (for development and building)
- **RobotHub Inference Server** running on target URL
- **RobotHub Transport Server** for communication rooms

## Communication Architecture

The inference server uses the RobotHub communication system:

1. **Camera Rooms**: Receive video streams (supports multiple cameras)
2. **Joint Input Room**: Receives current robot joint positions (normalized -100 to +100)
3. **Joint Output Room**: Sends predicted joint commands (normalized -100 to +100)

All rooms are created in the same workspace for session isolation.

## Error Handling

All client methods throw descriptive errors on failure:

```typescript
try {
  await client.createSession(request);
} catch (error) {
  console.error('Session creation failed:', error.message);
}
```

## Contributing

This client is auto-generated from the OpenAPI specification. To make changes:

1. Update the inference server's FastAPI endpoints
2. Regenerate the client: `bun run generate`
3. Update examples and documentation as needed

## License

Apache 2.0 - See LICENSE file for details.
