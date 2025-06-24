#!/usr/bin/env bun
/**
 * Basic Usage Example for LeRobot Arena Inference Server TypeScript Client
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
  LeRobotInferenceServerClient
} from '../src/index';

import type { 
  CreateSessionRequest,
  SessionStatusResponse 
} from '../src/generated';

async function main() {
  // Create client instance
  const client = new LeRobotInferenceServerClient('http://localhost:8001');

  try {
    console.log('🔍 Checking server health...');
    const isHealthy = await client.isHealthy();
    if (!isHealthy) {
      console.error('❌ Server is not healthy. Make sure the inference server is running.');
      process.exit(1);
    }
    console.log('✅ Server is healthy!');

    // Get detailed health info
    const healthInfo = await client.getHealth();
    console.log('📊 Server status:', healthInfo);

    // Create a session (using generated types)
    const sessionRequest: CreateSessionRequest = {
      session_id: 'example-session-' + Date.now(),
      policy_path: './checkpoints/act_so101_beyond', // Update with your model path
      camera_names: ['front', 'wrist'], // Update with your camera names
      arena_server_url: 'http://localhost:8000', // Update with your arena server URL
      workspace_id: null // Let the server generate a workspace ID
    };

    console.log('🚀 Creating inference session...');
    const session = await client.createSession(sessionRequest);
    console.log('✅ Session created!');
    console.log('📍 Workspace ID:', session.workspace_id);
    console.log('📷 Camera rooms:', session.camera_room_ids);
    console.log('🔄 Joint input room:', session.joint_input_room_id);
    console.log('🎯 Joint output room:', session.joint_output_room_id);

    // Start inference
    console.log('▶️ Starting inference...');
    await client.startInference(sessionRequest.session_id);
    console.log('✅ Inference started!');

    // Wait for the session to be running
    console.log('⏳ Waiting for session to be running...');
    const runningStatus = await client.waitForSessionStatus(
      sessionRequest.session_id, 
      'running', 
      30000 // 30 second timeout
    );
    console.log('🏃 Session is now running!');

    // Monitor the session for a few seconds
    console.log('📊 Monitoring session status...');
    for (let i = 0; i < 5; i++) {
      const status: SessionStatusResponse = await client.getSessionStatus(sessionRequest.session_id);
      console.log(`📈 Status: ${status.status}, Stats:`, status.stats);
      
      // Wait 2 seconds before next check
      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    // Get system info for debugging
    console.log('🔧 Getting system information...');
    const systemInfo = await client.getSystemInfo();
    console.log('💻 System info:', systemInfo);

    // Get session queue info
    console.log('📋 Getting session queue info...');
    const queueInfo = await client.getSessionQueueInfo(sessionRequest.session_id);
    console.log('📝 Queue info:', queueInfo);

    // Stop inference
    console.log('⏹️ Stopping inference...');
    await client.stopInference(sessionRequest.session_id);
    console.log('✅ Inference stopped!');

    // Clean up - delete the session
    console.log('🧹 Cleaning up session...');
    await client.deleteSession(sessionRequest.session_id);
    console.log('✅ Session deleted!');

    console.log('🎉 Example completed successfully!');

  } catch (error) {
    console.error('❌ Error:', error);
    process.exit(1);
  }
}

// Alternative: Using the convenience function
async function quickExample() {
  const client = new LeRobotInferenceServerClient('http://localhost:8001');

  try {
    // This creates a session and starts inference in one call
    const result = await client.createAndStartSession({
      session_id: 'quick-example-' + Date.now(),
      policy_path: './checkpoints/act_so101_beyond',
      camera_names: ['front'],
      arena_server_url: 'http://localhost:8000'
    });

    console.log('🚀 Quick session created and started!');
    console.log('Session:', result.session);
    console.log('Status:', result.status);

    // Clean up
    await client.deleteSession(result.status.session_id);
    console.log('✅ Quick example completed!');

  } catch (error) {
    console.error('❌ Quick example error:', error);
  }
}

// Run the main example
if (import.meta.main) {
  console.log('=== LeRobot Arena Inference Server Client Example ===\n');
  
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