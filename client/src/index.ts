/**
 * LeRobot Arena Inference Server TypeScript Client
 * 
 * This client provides TypeScript access to the LeRobot Arena Inference Server
 * for ACT (Action Chunking Transformer) model inference and session management.
 * 
 * @example Basic Usage
 * ```typescript
 * import { LeRobotInferenceServerClient, CreateSessionRequest } from '@lerobot-arena/inference-server-client';
 * 
 * const client = new LeRobotInferenceServerClient('http://localhost:8001');
 * 
 * // Create and start a session
 * const sessionRequest: CreateSessionRequest = {
 *   session_id: 'my-robot-01',
 *   policy_path: './checkpoints/act_so101_beyond',
 *   camera_names: ['front', 'wrist'],
 *   arena_server_url: 'http://localhost:8000'
 * };
 * 
 * const session = await client.createSession(sessionRequest);
 * await client.startInference('my-robot-01');
 * 
 * // Monitor session
 * const status = await client.getSessionStatus('my-robot-01');
 * console.log(`Session status: ${status.status}`);
 * ```
 */

// Export all generated types and services from OpenAPI
export * from './generated';

// Import what we need for the convenience wrapper
import { 
  client,
  createSessionSessionsPost,
  listSessionsSessionsGet,
  getSessionStatusSessionsSessionIdGet,
  startInferenceSessionsSessionIdStartPost,
  stopInferenceSessionsSessionIdStopPost,
  restartInferenceSessionsSessionIdRestartPost,
  deleteSessionSessionsSessionIdDelete,
  healthCheckHealthGet,
  getSystemInfoDebugSystemGet,
  debugResetSessionDebugSessionsSessionIdResetPost,
  getSessionQueueInfoDebugSessionsSessionIdQueueGet
} from './generated';

import type {
  CreateSessionRequest,
  CreateSessionResponse,
  SessionStatusResponse
} from './generated';

/**
 * LeRobot Arena Inference Server Client
 * 
 * A convenience wrapper around the generated OpenAPI client that provides
 * a simpler interface for common operations while maintaining full type safety.
 */
export class LeRobotInferenceServerClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    // Configure the generated client with the base URL
    client.setConfig({ baseUrl });
  }

  /**
   * Check if the inference server is healthy and responding
   */
  async isHealthy(): Promise<boolean> {
    try {
      const response = await healthCheckHealthGet();
      return !response.error;
    } catch {
      return false;
    }
  }

  /**
   * Get detailed server health information
   */
  async getHealth() {
    const response = await healthCheckHealthGet();
    if (response.error) {
      throw new Error(`Health check failed: ${JSON.stringify(response.error)}`);
    }
    return response.data;
  }

  /**
   * Create a new inference session
   */
  async createSession(request: CreateSessionRequest): Promise<CreateSessionResponse> {
    const response = await createSessionSessionsPost({
      body: request
    });

    if (response.error) {
      throw new Error(`Failed to create session: ${JSON.stringify(response.error)}`);
    }

    return response.data!;
  }

  /**
   * List all active sessions
   */
  async listSessions(): Promise<SessionStatusResponse[]> {
    const response = await listSessionsSessionsGet();
    if (response.error) {
      throw new Error(`Failed to list sessions: ${JSON.stringify(response.error)}`);
    }
    return response.data!;
  }

  /**
   * Get detailed status of a specific session
   */
  async getSessionStatus(sessionId: string): Promise<SessionStatusResponse> {
    const response = await getSessionStatusSessionsSessionIdGet({
      path: { session_id: sessionId }
    });

    if (response.error) {
      throw new Error(`Failed to get session status: ${JSON.stringify(response.error)}`);
    }

    return response.data!;
  }

  /**
   * Start inference for a session
   */
  async startInference(sessionId: string): Promise<void> {
    const response = await startInferenceSessionsSessionIdStartPost({
      path: { session_id: sessionId }
    });

    if (response.error) {
      throw new Error(`Failed to start inference: ${JSON.stringify(response.error)}`);
    }
  }

  /**
   * Stop inference for a session
   */
  async stopInference(sessionId: string): Promise<void> {
    const response = await stopInferenceSessionsSessionIdStopPost({
      path: { session_id: sessionId }
    });

    if (response.error) {
      throw new Error(`Failed to stop inference: ${JSON.stringify(response.error)}`);
    }
  }

  /**
   * Restart inference for a session
   */
  async restartInference(sessionId: string): Promise<void> {
    const response = await restartInferenceSessionsSessionIdRestartPost({
      path: { session_id: sessionId }
    });

    if (response.error) {
      throw new Error(`Failed to restart inference: ${JSON.stringify(response.error)}`);
    }
  }

  /**
   * Delete a session and clean up all resources
   */
  async deleteSession(sessionId: string): Promise<void> {
    const response = await deleteSessionSessionsSessionIdDelete({
      path: { session_id: sessionId }
    });

    if (response.error) {
      throw new Error(`Failed to delete session: ${JSON.stringify(response.error)}`);
    }
  }

  /**
   * Wait for a session to reach a specific status
   */
  async waitForSessionStatus(
    sessionId: string, 
    targetStatus: string, 
    timeoutMs: number = 30000
  ): Promise<SessionStatusResponse> {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeoutMs) {
      const status = await this.getSessionStatus(sessionId);
      if (status.status === targetStatus) {
        return status;
      }
      
      // Wait 1 second before checking again
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    throw new Error(`Timeout waiting for session ${sessionId} to reach status ${targetStatus}`);
  }

  /**
   * Convenience method to create a session and start inference in one call
   */
  async createAndStartSession(request: CreateSessionRequest): Promise<{
    session: CreateSessionResponse;
    status: SessionStatusResponse;
  }> {
    const session = await this.createSession(request);
    await this.startInference(request.session_id);
    
    // Wait for it to be running
    const status = await this.waitForSessionStatus(request.session_id, 'running');
    
    return { session, status };
  }

  /**
   * Get system information for debugging
   */
  async getSystemInfo() {
    const response = await getSystemInfoDebugSystemGet();
    if (response.error) {
      throw new Error(`Failed to get system info: ${JSON.stringify(response.error)}`);
    }
    return response.data;
  }

  /**
   * Reset a session's internal state (debug method)
   */
  async debugResetSession(sessionId: string): Promise<void> {
    const response = await debugResetSessionDebugSessionsSessionIdResetPost({
      path: { session_id: sessionId }
    });

    if (response.error) {
      throw new Error(`Failed to reset session: ${JSON.stringify(response.error)}`);
    }
  }

  /**
   * Get detailed information about a session's action queue
   */
  async getSessionQueueInfo(sessionId: string) {
    const response = await getSessionQueueInfoDebugSessionsSessionIdQueueGet({
      path: { session_id: sessionId }
    });

    if (response.error) {
      throw new Error(`Failed to get queue info: ${JSON.stringify(response.error)}`);
    }
    return response.data;
  }
}

// Convenience function to create a client
export function createClient(baseUrl: string): LeRobotInferenceServerClient {
  return new LeRobotInferenceServerClient(baseUrl);
}

// Export the old class name for backward compatibility
export const LeRobotAIServerClient = LeRobotInferenceServerClient; 