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
export * from './generated';
import type { CreateSessionRequest, CreateSessionResponse, SessionStatusResponse } from './generated';
/**
 * LeRobot Arena Inference Server Client
 *
 * A convenience wrapper around the generated OpenAPI client that provides
 * a simpler interface for common operations while maintaining full type safety.
 */
export declare class LeRobotInferenceServerClient {
    private baseUrl;
    constructor(baseUrl: string);
    /**
     * Check if the inference server is healthy and responding
     */
    isHealthy(): Promise<boolean>;
    /**
     * Get detailed server health information
     */
    getHealth(): Promise<unknown>;
    /**
     * Create a new inference session
     */
    createSession(request: CreateSessionRequest): Promise<CreateSessionResponse>;
    /**
     * List all active sessions
     */
    listSessions(): Promise<SessionStatusResponse[]>;
    /**
     * Get detailed status of a specific session
     */
    getSessionStatus(sessionId: string): Promise<SessionStatusResponse>;
    /**
     * Start inference for a session
     */
    startInference(sessionId: string): Promise<void>;
    /**
     * Stop inference for a session
     */
    stopInference(sessionId: string): Promise<void>;
    /**
     * Restart inference for a session
     */
    restartInference(sessionId: string): Promise<void>;
    /**
     * Delete a session and clean up all resources
     */
    deleteSession(sessionId: string): Promise<void>;
    /**
     * Wait for a session to reach a specific status
     */
    waitForSessionStatus(sessionId: string, targetStatus: string, timeoutMs?: number): Promise<SessionStatusResponse>;
    /**
     * Convenience method to create a session and start inference in one call
     */
    createAndStartSession(request: CreateSessionRequest): Promise<{
        session: CreateSessionResponse;
        status: SessionStatusResponse;
    }>;
    /**
     * Get system information for debugging
     */
    getSystemInfo(): Promise<unknown>;
    /**
     * Reset a session's internal state (debug method)
     */
    debugResetSession(sessionId: string): Promise<void>;
    /**
     * Get detailed information about a session's action queue
     */
    getSessionQueueInfo(sessionId: string): Promise<unknown>;
}
export declare function createClient(baseUrl: string): LeRobotInferenceServerClient;
export declare const LeRobotAIServerClient: typeof LeRobotInferenceServerClient;
//# sourceMappingURL=index.d.ts.map