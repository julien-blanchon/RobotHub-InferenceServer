import { type Options } from '@hey-api/client-fetch';
import type { ListSessionsSessionsGetResponse, CreateSessionSessionsPostData, GetSessionStatusSessionsSessionIdGetData, DeleteSessionSessionsSessionIdDeleteData, StartInferenceSessionsSessionIdStartPostData, StopInferenceSessionsSessionIdStopPostData, RestartInferenceSessionsSessionIdRestartPostData, DebugResetSessionDebugSessionsSessionIdResetPostData, GetSessionQueueInfoDebugSessionsSessionIdQueueGetData } from './types.gen';
export declare const client: import("@hey-api/client-fetch").Client<Request, Response, import("@hey-api/client-fetch").RequestOptions>;
/**
 * Root
 * Health check endpoint.
 */
export declare const rootGet: <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => import("@hey-api/client-fetch").RequestResult<unknown, unknown, ThrowOnError>;
/**
 * Health Check
 * Detailed health check.
 */
export declare const healthCheckHealthGet: <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => import("@hey-api/client-fetch").RequestResult<unknown, unknown, ThrowOnError>;
/**
 * List Policies
 * List supported policy types.
 */
export declare const listPoliciesPoliciesGet: <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => import("@hey-api/client-fetch").RequestResult<unknown, unknown, ThrowOnError>;
/**
 * List Sessions
 * List all sessions.
 */
export declare const listSessionsSessionsGet: <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => import("@hey-api/client-fetch").RequestResult<ListSessionsSessionsGetResponse, unknown, ThrowOnError>;
/**
 * Create Session
 * Create a new inference session.
 *
 * If workspace_id is provided, all rooms will be created in that workspace.
 * If workspace_id is not provided, a new workspace will be generated automatically.
 * All rooms for a session (cameras + joints) are always created in the same workspace.
 */
export declare const createSessionSessionsPost: <ThrowOnError extends boolean = false>(options: Options<CreateSessionSessionsPostData, ThrowOnError>) => import("@hey-api/client-fetch").RequestResult<import("./types.gen").CreateSessionResponse, import("./types.gen").HTTPValidationError, ThrowOnError>;
/**
 * Get Session Status
 * Get status of a specific session.
 */
export declare const getSessionStatusSessionsSessionIdGet: <ThrowOnError extends boolean = false>(options: Options<GetSessionStatusSessionsSessionIdGetData, ThrowOnError>) => import("@hey-api/client-fetch").RequestResult<import("./types.gen").SessionStatusResponse, import("./types.gen").HTTPValidationError, ThrowOnError>;
/**
 * Delete Session
 * Delete a session.
 */
export declare const deleteSessionSessionsSessionIdDelete: <ThrowOnError extends boolean = false>(options: Options<DeleteSessionSessionsSessionIdDeleteData, ThrowOnError>) => import("@hey-api/client-fetch").RequestResult<unknown, import("./types.gen").HTTPValidationError, ThrowOnError>;
/**
 * Start Inference
 * Start inference for a session.
 */
export declare const startInferenceSessionsSessionIdStartPost: <ThrowOnError extends boolean = false>(options: Options<StartInferenceSessionsSessionIdStartPostData, ThrowOnError>) => import("@hey-api/client-fetch").RequestResult<unknown, import("./types.gen").HTTPValidationError, ThrowOnError>;
/**
 * Stop Inference
 * Stop inference for a session.
 */
export declare const stopInferenceSessionsSessionIdStopPost: <ThrowOnError extends boolean = false>(options: Options<StopInferenceSessionsSessionIdStopPostData, ThrowOnError>) => import("@hey-api/client-fetch").RequestResult<unknown, import("./types.gen").HTTPValidationError, ThrowOnError>;
/**
 * Restart Inference
 * Restart inference for a session.
 */
export declare const restartInferenceSessionsSessionIdRestartPost: <ThrowOnError extends boolean = false>(options: Options<RestartInferenceSessionsSessionIdRestartPostData, ThrowOnError>) => import("@hey-api/client-fetch").RequestResult<unknown, import("./types.gen").HTTPValidationError, ThrowOnError>;
/**
 * Get System Info
 * Get system information for debugging.
 */
export declare const getSystemInfoDebugSystemGet: <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => import("@hey-api/client-fetch").RequestResult<unknown, unknown, ThrowOnError>;
/**
 * Get Recent Logs
 * Get recent log entries for debugging.
 */
export declare const getRecentLogsDebugLogsGet: <ThrowOnError extends boolean = false>(options?: Options<unknown, ThrowOnError>) => import("@hey-api/client-fetch").RequestResult<unknown, unknown, ThrowOnError>;
/**
 * Debug Reset Session
 * Reset a session's internal state for debugging.
 */
export declare const debugResetSessionDebugSessionsSessionIdResetPost: <ThrowOnError extends boolean = false>(options: Options<DebugResetSessionDebugSessionsSessionIdResetPostData, ThrowOnError>) => import("@hey-api/client-fetch").RequestResult<unknown, import("./types.gen").HTTPValidationError, ThrowOnError>;
/**
 * Get Session Queue Info
 * Get detailed information about a session's action queue.
 */
export declare const getSessionQueueInfoDebugSessionsSessionIdQueueGet: <ThrowOnError extends boolean = false>(options: Options<GetSessionQueueInfoDebugSessionsSessionIdQueueGetData, ThrowOnError>) => import("@hey-api/client-fetch").RequestResult<unknown, import("./types.gen").HTTPValidationError, ThrowOnError>;
//# sourceMappingURL=services.gen.d.ts.map