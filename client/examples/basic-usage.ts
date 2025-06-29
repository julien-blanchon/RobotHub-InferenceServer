#!/usr/bin/env bun
/**
 * Basic Usage Example for RobotHub Inference Server TypeScript Client
 * 
 * This example demonstrates how to:
 * 1. Create a client instance
 * 2. Check server health
 * 3. Create an inference session
 * 4. Start inference
 * 5. Monitor session status
 * 6. Clean up resources
 */

import { 
  rootGet,
  healthCheckHealthGet,
  listSessionsSessionsGet,
  createSessionSessionsPost,
  startInferenceSessionsSessionIdStartPost,
  stopInferenceSessionsSessionIdStopPost,
  deleteSessionSessionsSessionIdDelete
} from '../src';

import type { 
  CreateSessionRequest,
  SessionStatusResponse 
} from '../src';

// Configuration
const BASE_URL = 'http://localhost:8001/api';

// Helper function to wait for a specific session status
async function waitForSessionStatus(
  sessionId: string, 
  targetStatus: string, 
  timeoutMs: number = 30000
): Promise<SessionStatusResponse> {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeoutMs) {
    const sessions = await listSessionsSessionsGet({ baseUrl: BASE_URL });
    const session = sessions.data?.find(s => s.session_id === sessionId);
    
    if (session && session.status === targetStatus) {
      return session;
    }
    
    if (session && session.status === 'error') {
      throw new Error(`Session failed: ${session.error_message}`);
    }
    
    // Wait 1 second before checking again
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  throw new Error(`Timeout waiting for session ${sessionId} to reach status ${targetStatus}`);
}

// Helper function to get session status
async function getSessionStatus(sessionId: string): Promise<SessionStatusResponse> {
  const sessions = await listSessionsSessionsGet({ baseUrl: BASE_URL });
  const session = sessions.data?.find(s => s.session_id === sessionId);
  
  if (!session) {
    throw new Error(`Session ${sessionId} not found`);
  }
  
  return session;
}

async function main() {
  try {
    console.log('🔍 Checking server health...');
    const healthResponse = await rootGet({ baseUrl: BASE_URL });
    if (!healthResponse.data) {
      console.error('❌ Server is not healthy. Make sure the inference server is running.');
      process.exit(1);
    }
    console.log('✅ Server is healthy!');

    // Get detailed health info
    console.log('📊 Getting detailed server status...');
    const detailedHealth = await healthCheckHealthGet({ baseUrl: BASE_URL });
    console.log('📊 Server status:', detailedHealth.data);

    // Create a session (using generated types)
    const sessionRequest: CreateSessionRequest = {
      session_id: 'example-session-' + Date.now(),
      policy_path: 'LaetusH/act_so101_beyond', // HuggingFace repo format
      camera_names: ['front', 'wrist'], // Update with your camera names
      transport_server_url: 'http://localhost:8000', // Update with your transport server URL
      workspace_id: null, // Let the server generate a workspace ID
      policy_type: 'act',
      language_instruction: null
    };

    console.log('🚀 Creating inference session...');
    const sessionResponse = await createSessionSessionsPost({
      body: sessionRequest,
      baseUrl: BASE_URL
    });
    
    if (!sessionResponse.data) {
      throw new Error('Failed to create session');
    }
    
    const session = sessionResponse.data;
    console.log('✅ Session created!');
    console.log('📍 Workspace ID:', session.workspace_id);
    console.log('📷 Camera rooms:', session.camera_room_ids);
    console.log('🔄 Joint input room:', session.joint_input_room_id);
    console.log('🎯 Joint output room:', session.joint_output_room_id);

    // Start inference
    console.log('▶️ Starting inference...');
    await startInferenceSessionsSessionIdStartPost({
      path: { session_id: sessionRequest.session_id },
      baseUrl: BASE_URL
    });
    console.log('✅ Inference started!');

    // Wait for the session to be running
    console.log('⏳ Waiting for session to be running...');
    const runningStatus = await waitForSessionStatus(
      sessionRequest.session_id, 
      'running', 
      30000 // 30 second timeout
    );
    console.log('🏃 Session is now running!');

    // Monitor the session for a few seconds
    console.log('📊 Monitoring session status...');
    for (let i = 0; i < 5; i++) {
      const status: SessionStatusResponse = await getSessionStatus(sessionRequest.session_id);
      console.log(`📈 Status: ${status.status}, Stats:`, status.stats);
      
      // Wait 2 seconds before next check
      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    // List all sessions for debugging
    console.log('📋 Getting all sessions...');
    const allSessions = await listSessionsSessionsGet({ baseUrl: BASE_URL });
    console.log('📝 All sessions:', allSessions.data?.map(s => ({
      id: s.session_id,
      status: s.status,
      policy_path: s.policy_path
    })));

    // Stop inference
    console.log('⏹️ Stopping inference...');
    await stopInferenceSessionsSessionIdStopPost({
      path: { session_id: sessionRequest.session_id },
      baseUrl: BASE_URL
    });
    console.log('✅ Inference stopped!');

    // Clean up - delete the session
    console.log('🧹 Cleaning up session...');
    await deleteSessionSessionsSessionIdDelete({
      path: { session_id: sessionRequest.session_id },
      baseUrl: BASE_URL
    });
    console.log('✅ Session deleted!');

    console.log('🎉 Example completed successfully!');

  } catch (error) {
    console.error('❌ Error:', error);
    process.exit(1);
  }
}

// Alternative: Using a more streamlined approach
async function quickExample() {
  try {
    // Test health first
    console.log('🔍 Testing server health...');
    const healthResponse = await rootGet({ baseUrl: BASE_URL });
    if (!healthResponse.data) {
      throw new Error('Server health check failed');
    }
    console.log('✅ Server is healthy!');
    
    // Create session
    const sessionId = 'quick-example-' + Date.now();
    console.log('🚀 Creating session...');
    
    const sessionResponse = await createSessionSessionsPost({
      body: {
        session_id: sessionId,
        policy_path: 'LaetusH/act_so101_beyond', // HuggingFace repo format
        camera_names: ['front'],
        transport_server_url: 'http://localhost:8000'
      },
      baseUrl: BASE_URL
    });

    if (!sessionResponse.data) {
      throw new Error(`Failed to create session: ${sessionResponse.error?.detail || 'Unknown error'}`);
    }

    console.log('✅ Session created!');
    console.log('📍 Workspace ID:', sessionResponse.data.workspace_id);
    console.log('📷 Camera rooms:', sessionResponse.data.camera_room_ids);

    // Start inference
    console.log('▶️ Starting inference...');
    await startInferenceSessionsSessionIdStartPost({
      path: { session_id: sessionId },
      baseUrl: BASE_URL
    });
    console.log('✅ Inference started!');

    // Wait a moment then get status
    console.log('📊 Checking status...');
    await new Promise(resolve => setTimeout(resolve, 2000));
    const status = await getSessionStatus(sessionId);
    console.log(`📈 Status: ${status.status}`);
    console.log('📊 Stats:', status.stats);

    // Clean up
    console.log('🧹 Cleaning up...');
    await deleteSessionSessionsSessionIdDelete({
      path: { session_id: sessionId },
      baseUrl: BASE_URL
    });
    console.log('✅ Quick example completed!');

  } catch (error) {
    console.error('❌ Quick example error:', error);
  }
}

// Run the main example
if (import.meta.main) {
  console.log('=== RobotHub Inference Server Client Example ===\n');
  
  // Choose which example to run based on command line argument
  const runQuick = process.argv.includes('--quick');
  
  if (runQuick) {
    console.log('Running quick example...\n');
    await quickExample();
  } else {
    console.log('Running full example...\n');
    await main();
  }
} 