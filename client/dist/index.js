// @bun
var __create = Object.create;
var __getProtoOf = Object.getPrototypeOf;
var __defProp = Object.defineProperty;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __toESM = (mod, isNodeMode, target) => {
  target = mod != null ? __create(__getProtoOf(mod)) : {};
  const to = isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target;
  for (let key of __getOwnPropNames(mod))
    if (!__hasOwnProp.call(to, key))
      __defProp(to, key, {
        get: () => mod[key],
        enumerable: true
      });
  return to;
};
var __commonJS = (cb, mod) => () => (mod || cb((mod = { exports: {} }).exports, mod), mod.exports);
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, {
      get: all[name],
      enumerable: true,
      configurable: true,
      set: (newValue) => all[name] = () => newValue
    });
};

// ../../../../node_modules/eventemitter3/index.js
var require_eventemitter3 = __commonJS((exports, module) => {
  var has = Object.prototype.hasOwnProperty;
  var prefix = "~";
  function Events() {}
  if (Object.create) {
    Events.prototype = Object.create(null);
    if (!new Events().__proto__)
      prefix = false;
  }
  function EE(fn, context, once) {
    this.fn = fn;
    this.context = context;
    this.once = once || false;
  }
  function addListener(emitter, event, fn, context, once) {
    if (typeof fn !== "function") {
      throw new TypeError("The listener must be a function");
    }
    var listener = new EE(fn, context || emitter, once), evt = prefix ? prefix + event : event;
    if (!emitter._events[evt])
      emitter._events[evt] = listener, emitter._eventsCount++;
    else if (!emitter._events[evt].fn)
      emitter._events[evt].push(listener);
    else
      emitter._events[evt] = [emitter._events[evt], listener];
    return emitter;
  }
  function clearEvent(emitter, evt) {
    if (--emitter._eventsCount === 0)
      emitter._events = new Events;
    else
      delete emitter._events[evt];
  }
  function EventEmitter() {
    this._events = new Events;
    this._eventsCount = 0;
  }
  EventEmitter.prototype.eventNames = function eventNames() {
    var names = [], events, name;
    if (this._eventsCount === 0)
      return names;
    for (name in events = this._events) {
      if (has.call(events, name))
        names.push(prefix ? name.slice(1) : name);
    }
    if (Object.getOwnPropertySymbols) {
      return names.concat(Object.getOwnPropertySymbols(events));
    }
    return names;
  };
  EventEmitter.prototype.listeners = function listeners(event) {
    var evt = prefix ? prefix + event : event, handlers = this._events[evt];
    if (!handlers)
      return [];
    if (handlers.fn)
      return [handlers.fn];
    for (var i = 0, l = handlers.length, ee = new Array(l);i < l; i++) {
      ee[i] = handlers[i].fn;
    }
    return ee;
  };
  EventEmitter.prototype.listenerCount = function listenerCount(event) {
    var evt = prefix ? prefix + event : event, listeners = this._events[evt];
    if (!listeners)
      return 0;
    if (listeners.fn)
      return 1;
    return listeners.length;
  };
  EventEmitter.prototype.emit = function emit(event, a1, a2, a3, a4, a5) {
    var evt = prefix ? prefix + event : event;
    if (!this._events[evt])
      return false;
    var listeners = this._events[evt], len = arguments.length, args, i;
    if (listeners.fn) {
      if (listeners.once)
        this.removeListener(event, listeners.fn, undefined, true);
      switch (len) {
        case 1:
          return listeners.fn.call(listeners.context), true;
        case 2:
          return listeners.fn.call(listeners.context, a1), true;
        case 3:
          return listeners.fn.call(listeners.context, a1, a2), true;
        case 4:
          return listeners.fn.call(listeners.context, a1, a2, a3), true;
        case 5:
          return listeners.fn.call(listeners.context, a1, a2, a3, a4), true;
        case 6:
          return listeners.fn.call(listeners.context, a1, a2, a3, a4, a5), true;
      }
      for (i = 1, args = new Array(len - 1);i < len; i++) {
        args[i - 1] = arguments[i];
      }
      listeners.fn.apply(listeners.context, args);
    } else {
      var length = listeners.length, j;
      for (i = 0;i < length; i++) {
        if (listeners[i].once)
          this.removeListener(event, listeners[i].fn, undefined, true);
        switch (len) {
          case 1:
            listeners[i].fn.call(listeners[i].context);
            break;
          case 2:
            listeners[i].fn.call(listeners[i].context, a1);
            break;
          case 3:
            listeners[i].fn.call(listeners[i].context, a1, a2);
            break;
          case 4:
            listeners[i].fn.call(listeners[i].context, a1, a2, a3);
            break;
          default:
            if (!args)
              for (j = 1, args = new Array(len - 1);j < len; j++) {
                args[j - 1] = arguments[j];
              }
            listeners[i].fn.apply(listeners[i].context, args);
        }
      }
    }
    return true;
  };
  EventEmitter.prototype.on = function on(event, fn, context) {
    return addListener(this, event, fn, context, false);
  };
  EventEmitter.prototype.once = function once(event, fn, context) {
    return addListener(this, event, fn, context, true);
  };
  EventEmitter.prototype.removeListener = function removeListener(event, fn, context, once) {
    var evt = prefix ? prefix + event : event;
    if (!this._events[evt])
      return this;
    if (!fn) {
      clearEvent(this, evt);
      return this;
    }
    var listeners = this._events[evt];
    if (listeners.fn) {
      if (listeners.fn === fn && (!once || listeners.once) && (!context || listeners.context === context)) {
        clearEvent(this, evt);
      }
    } else {
      for (var i = 0, events = [], length = listeners.length;i < length; i++) {
        if (listeners[i].fn !== fn || once && !listeners[i].once || context && listeners[i].context !== context) {
          events.push(listeners[i]);
        }
      }
      if (events.length)
        this._events[evt] = events.length === 1 ? events[0] : events;
      else
        clearEvent(this, evt);
    }
    return this;
  };
  EventEmitter.prototype.removeAllListeners = function removeAllListeners(event) {
    var evt;
    if (event) {
      evt = prefix ? prefix + event : event;
      if (this._events[evt])
        clearEvent(this, evt);
    } else {
      this._events = new Events;
      this._eventsCount = 0;
    }
    return this;
  };
  EventEmitter.prototype.off = EventEmitter.prototype.removeListener;
  EventEmitter.prototype.addListener = EventEmitter.prototype.on;
  EventEmitter.prefixed = prefix;
  EventEmitter.EventEmitter = EventEmitter;
  if (typeof module !== "undefined") {
    module.exports = EventEmitter;
  }
});

// src/robotics/index.ts
var exports_robotics = {};
__export(exports_robotics, {
  createProducerClient: () => createProducerClient,
  createConsumerClient: () => createConsumerClient,
  createClient: () => createClient,
  RoboticsProducer: () => RoboticsProducer,
  RoboticsConsumer: () => RoboticsConsumer,
  RoboticsClientCore: () => RoboticsClientCore
});

// ../../../../node_modules/eventemitter3/index.mjs
var import__ = __toESM(require_eventemitter3(), 1);

// src/robotics/core.ts
class RoboticsClientCore extends import__.default {
  baseUrl;
  apiBase;
  websocket = null;
  workspaceId = null;
  roomId = null;
  role = null;
  participantId = null;
  connected = false;
  options;
  onErrorCallback = null;
  onConnectedCallback = null;
  onDisconnectedCallback = null;
  constructor(baseUrl = "http://localhost:8000", options = {}) {
    super();
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.apiBase = `${this.baseUrl}/robotics`;
    this.options = {
      timeout: 5000,
      reconnect_attempts: 3,
      heartbeat_interval: 30000,
      ...options
    };
  }
  async listRooms(workspaceId) {
    const response = await this.fetchApi(`/workspaces/${workspaceId}/rooms`);
    return response.rooms;
  }
  async createRoom(workspaceId, roomId) {
    const finalWorkspaceId = workspaceId || this.generateWorkspaceId();
    const payload = roomId ? { room_id: roomId, workspace_id: finalWorkspaceId } : { workspace_id: finalWorkspaceId };
    const response = await this.fetchApi(`/workspaces/${finalWorkspaceId}/rooms`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    return { workspaceId: response.workspace_id, roomId: response.room_id };
  }
  async deleteRoom(workspaceId, roomId) {
    try {
      const response = await this.fetchApi(`/workspaces/${workspaceId}/rooms/${roomId}`, {
        method: "DELETE"
      });
      return response.success;
    } catch (error) {
      if (error instanceof Error && error.message.includes("404")) {
        return false;
      }
      throw error;
    }
  }
  async getRoomState(workspaceId, roomId) {
    const response = await this.fetchApi(`/workspaces/${workspaceId}/rooms/${roomId}/state`);
    return response.state;
  }
  async getRoomInfo(workspaceId, roomId) {
    const response = await this.fetchApi(`/workspaces/${workspaceId}/rooms/${roomId}`);
    return response.room;
  }
  async connectToRoom(workspaceId, roomId, role, participantId) {
    if (this.connected) {
      await this.disconnect();
    }
    this.workspaceId = workspaceId;
    this.roomId = roomId;
    this.role = role;
    this.participantId = participantId || `${role}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const wsUrl = this.baseUrl.replace(/^http/, "ws").replace(/^https/, "wss");
    const wsEndpoint = `${wsUrl}/robotics/workspaces/${workspaceId}/rooms/${roomId}/ws`;
    try {
      this.websocket = new WebSocket(wsEndpoint);
      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error("Connection timeout"));
        }, this.options.timeout || 5000);
        this.websocket.onopen = () => {
          clearTimeout(timeout);
          this.sendJoinMessage();
        };
        this.websocket.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
            if (message.type === "joined") {
              this.connected = true;
              this.onConnectedCallback?.();
              this.emit("connected");
              resolve(true);
            } else if (message.type === "error") {
              this.handleError(message.message);
              resolve(false);
            }
          } catch (error) {
            console.error("Failed to parse WebSocket message:", error);
          }
        };
        this.websocket.onerror = (error) => {
          clearTimeout(timeout);
          console.error("WebSocket error:", error);
          this.handleError("WebSocket connection error");
          reject(error);
        };
        this.websocket.onclose = () => {
          clearTimeout(timeout);
          this.connected = false;
          this.onDisconnectedCallback?.();
          this.emit("disconnected");
        };
      });
    } catch (error) {
      console.error("Failed to connect to room:", error);
      return false;
    }
  }
  async disconnect() {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.close();
    }
    this.websocket = null;
    this.connected = false;
    this.workspaceId = null;
    this.roomId = null;
    this.role = null;
    this.participantId = null;
    this.onDisconnectedCallback?.();
    this.emit("disconnected");
  }
  sendJoinMessage() {
    if (!this.websocket || !this.participantId || !this.role)
      return;
    const joinMessage = {
      participant_id: this.participantId,
      role: this.role
    };
    this.websocket.send(JSON.stringify(joinMessage));
  }
  handleMessage(message) {
    switch (message.type) {
      case "joined":
        console.log(`Successfully joined room ${message.room_id} as ${message.role}`);
        break;
      case "heartbeat_ack":
        console.debug("Heartbeat acknowledged");
        break;
      case "error":
        this.handleError(message.message);
        break;
      default:
        this.handleRoleSpecificMessage(message);
    }
  }
  handleRoleSpecificMessage(message) {
    this.emit("message", message);
  }
  handleError(errorMessage) {
    console.error("Client error:", errorMessage);
    this.onErrorCallback?.(errorMessage);
    this.emit("error", errorMessage);
  }
  async sendHeartbeat() {
    if (!this.connected || !this.websocket)
      return;
    const message = { type: "heartbeat" };
    this.websocket.send(JSON.stringify(message));
  }
  isConnected() {
    return this.connected;
  }
  getConnectionInfo() {
    return {
      connected: this.connected,
      workspace_id: this.workspaceId,
      room_id: this.roomId,
      role: this.role,
      participant_id: this.participantId,
      base_url: this.baseUrl
    };
  }
  onError(callback) {
    this.onErrorCallback = callback;
  }
  onConnected(callback) {
    this.onConnectedCallback = callback;
  }
  onDisconnected(callback) {
    this.onDisconnectedCallback = callback;
  }
  async fetchApi(endpoint, options = {}) {
    const url = `${this.apiBase}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      signal: AbortSignal.timeout(this.options.timeout || 5000)
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }
  generateWorkspaceId() {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === "x" ? r : r & 3 | 8;
      return v.toString(16);
    });
  }
}
// src/robotics/producer.ts
class RoboticsProducer extends RoboticsClientCore {
  constructor(baseUrl = "http://localhost:8000", options = {}) {
    super(baseUrl, options);
  }
  async connect(workspaceId, roomId, participantId) {
    return this.connectToRoom(workspaceId, roomId, "producer", participantId);
  }
  async sendJointUpdate(joints) {
    if (!this.connected || !this.websocket) {
      throw new Error("Must be connected to send joint updates");
    }
    const message = {
      type: "joint_update",
      data: joints,
      timestamp: new Date().toISOString()
    };
    this.websocket.send(JSON.stringify(message));
  }
  async sendStateSync(state) {
    if (!this.connected || !this.websocket) {
      throw new Error("Must be connected to send state sync");
    }
    const joints = Object.entries(state).map(([name, value]) => ({
      name,
      value
    }));
    await this.sendJointUpdate(joints);
  }
  async sendEmergencyStop(reason = "Emergency stop") {
    if (!this.connected || !this.websocket) {
      throw new Error("Must be connected to send emergency stop");
    }
    const message = {
      type: "emergency_stop",
      reason,
      timestamp: new Date().toISOString()
    };
    this.websocket.send(JSON.stringify(message));
  }
  handleRoleSpecificMessage(message) {
    switch (message.type) {
      case "emergency_stop":
        console.warn(`\uD83D\uDEA8 Emergency stop: ${message.reason || "Unknown reason"}`);
        this.handleError(`Emergency stop: ${message.reason || "Unknown reason"}`);
        break;
      case "error":
        console.error(`Server error: ${message.message}`);
        this.handleError(message.message);
        break;
      default:
        console.warn(`Unknown message type for producer: ${message.type}`);
    }
  }
  static async createAndConnect(baseUrl = "http://localhost:8000", workspaceId, roomId, participantId) {
    const producer = new RoboticsProducer(baseUrl);
    const roomData = await producer.createRoom(workspaceId, roomId);
    const connected = await producer.connect(roomData.workspaceId, roomData.roomId, participantId);
    if (!connected) {
      throw new Error("Failed to connect as producer");
    }
    return producer;
  }
  get currentRoomId() {
    return this.roomId;
  }
}
// src/robotics/consumer.ts
class RoboticsConsumer extends RoboticsClientCore {
  onStateSyncCallback = null;
  onJointUpdateCallback = null;
  constructor(baseUrl = "http://localhost:8000", options = {}) {
    super(baseUrl, options);
  }
  async connect(workspaceId, roomId, participantId) {
    return this.connectToRoom(workspaceId, roomId, "consumer", participantId);
  }
  async getStateSyncAsync() {
    if (!this.workspaceId || !this.roomId) {
      throw new Error("Must be connected to a room");
    }
    const state = await this.getRoomState(this.workspaceId, this.roomId);
    return state.joints;
  }
  onStateSync(callback) {
    this.onStateSyncCallback = callback;
  }
  onJointUpdate(callback) {
    this.onJointUpdateCallback = callback;
  }
  handleRoleSpecificMessage(message) {
    switch (message.type) {
      case "state_sync":
        this.handleStateSync(message);
        break;
      case "joint_update":
        this.handleJointUpdate(message);
        break;
      case "emergency_stop":
        console.warn(`\uD83D\uDEA8 Emergency stop: ${message.reason || "Unknown reason"}`);
        this.handleError(`Emergency stop: ${message.reason || "Unknown reason"}`);
        break;
      case "error":
        console.error(`Server error: ${message.message}`);
        this.handleError(message.message);
        break;
      default:
        console.warn(`Unknown message type for consumer: ${message.type}`);
    }
  }
  handleStateSync(message) {
    if (this.onStateSyncCallback) {
      this.onStateSyncCallback(message.data);
    }
    this.emit("stateSync", message.data);
  }
  handleJointUpdate(message) {
    if (this.onJointUpdateCallback) {
      this.onJointUpdateCallback(message.data);
    }
    this.emit("jointUpdate", message.data);
  }
  static async createAndConnect(workspaceId, roomId, baseUrl = "http://localhost:8000", participantId) {
    const consumer = new RoboticsConsumer(baseUrl);
    const connected = await consumer.connect(workspaceId, roomId, participantId);
    if (!connected) {
      throw new Error("Failed to connect as consumer");
    }
    return consumer;
  }
}
// src/robotics/factory.ts
function createClient(role, baseUrl = "http://localhost:8000", options = {}) {
  if (role === "producer") {
    return new RoboticsProducer(baseUrl, options);
  }
  if (role === "consumer") {
    return new RoboticsConsumer(baseUrl, options);
  }
  throw new Error(`Invalid role: ${role}. Must be 'producer' or 'consumer'`);
}
async function createProducerClient(baseUrl = "http://localhost:8000", workspaceId, roomId, participantId, options = {}) {
  const producer = new RoboticsProducer(baseUrl, options);
  const roomData = await producer.createRoom(workspaceId, roomId);
  const connected = await producer.connect(roomData.workspaceId, roomData.roomId, participantId);
  if (!connected) {
    throw new Error("Failed to connect as producer");
  }
  return producer;
}
async function createConsumerClient(workspaceId, roomId, baseUrl = "http://localhost:8000", participantId, options = {}) {
  const consumer = new RoboticsConsumer(baseUrl, options);
  const connected = await consumer.connect(workspaceId, roomId, participantId);
  if (!connected) {
    throw new Error("Failed to connect as consumer");
  }
  return consumer;
}
// src/video/index.ts
var exports_video = {};
__export(exports_video, {
  createProducerClient: () => createProducerClient2,
  createConsumerClient: () => createConsumerClient2,
  createClient: () => createClient2,
  VideoProducer: () => VideoProducer,
  VideoConsumer: () => VideoConsumer,
  VideoClientCore: () => VideoClientCore
});

// src/video/core.ts
class VideoClientCore extends import__.default {
  baseUrl;
  apiBase;
  websocket = null;
  peerConnection = null;
  localStream = null;
  remoteStream = null;
  workspaceId = null;
  roomId = null;
  role = null;
  participantId = null;
  connected = false;
  options;
  webrtcConfig;
  onErrorCallback = null;
  onConnectedCallback = null;
  onDisconnectedCallback = null;
  constructor(baseUrl = "http://localhost:8000", options = {}) {
    super();
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.apiBase = `${this.baseUrl}/video`;
    this.options = {
      timeout: 5000,
      reconnect_attempts: 3,
      heartbeat_interval: 30000,
      ...options
    };
    this.webrtcConfig = {
      iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
      constraints: {
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          frameRate: { ideal: 30 }
        },
        audio: false
      },
      bitrate: 1e6,
      framerate: 30,
      resolution: { width: 640, height: 480 },
      codecPreferences: ["VP8", "H264"],
      ...this.options.webrtc_config
    };
  }
  async listRooms(workspaceId) {
    const response = await this.fetchApi(`/workspaces/${workspaceId}/rooms`);
    return response.rooms;
  }
  async createRoom(workspaceId, roomId, config, recoveryConfig) {
    const finalWorkspaceId = workspaceId || this.generateWorkspaceId();
    const payload = {
      room_id: roomId,
      workspace_id: finalWorkspaceId,
      config,
      recovery_config: recoveryConfig
    };
    const response = await this.fetchApi(`/workspaces/${finalWorkspaceId}/rooms`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    return { workspaceId: response.workspace_id, roomId: response.room_id };
  }
  async deleteRoom(workspaceId, roomId) {
    try {
      const response = await this.fetchApi(`/workspaces/${workspaceId}/rooms/${roomId}`, {
        method: "DELETE"
      });
      return response.success;
    } catch (error) {
      if (error instanceof Error && error.message.includes("404")) {
        return false;
      }
      throw error;
    }
  }
  async getRoomState(workspaceId, roomId) {
    const response = await this.fetchApi(`/workspaces/${workspaceId}/rooms/${roomId}/state`);
    return response.state;
  }
  async getRoomInfo(workspaceId, roomId) {
    const response = await this.fetchApi(`/workspaces/${workspaceId}/rooms/${roomId}`);
    return response.room;
  }
  async sendWebRTCSignal(workspaceId, roomId, clientId, message) {
    const request = { client_id: clientId, message };
    return this.fetchApi(`/workspaces/${workspaceId}/rooms/${roomId}/webrtc/signal`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request)
    });
  }
  async connectToRoom(workspaceId, roomId, role, participantId) {
    if (this.connected) {
      await this.disconnect();
    }
    this.workspaceId = workspaceId;
    this.roomId = roomId;
    this.role = role;
    this.participantId = participantId || `${role}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const wsUrl = this.baseUrl.replace(/^http/, "ws").replace(/^https/, "wss");
    const wsEndpoint = `${wsUrl}/video/workspaces/${workspaceId}/rooms/${roomId}/ws`;
    try {
      this.websocket = new WebSocket(wsEndpoint);
      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error("Connection timeout"));
        }, this.options.timeout || 5000);
        this.websocket.onopen = () => {
          clearTimeout(timeout);
          this.sendJoinMessage();
        };
        this.websocket.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
            if (message.type === "joined") {
              this.connected = true;
              this.onConnectedCallback?.();
              this.emit("connected");
              resolve(true);
            } else if (message.type === "error") {
              this.handleError(message.message);
              resolve(false);
            }
          } catch (error) {
            console.error("Failed to parse WebSocket message:", error);
          }
        };
        this.websocket.onerror = (error) => {
          clearTimeout(timeout);
          console.error("WebSocket error:", error);
          this.handleError("WebSocket connection error");
          reject(error);
        };
        this.websocket.onclose = () => {
          clearTimeout(timeout);
          this.connected = false;
          this.onDisconnectedCallback?.();
          this.emit("disconnected");
        };
      });
    } catch (error) {
      console.error("Failed to connect to room:", error);
      return false;
    }
  }
  async disconnect() {
    if (this.peerConnection) {
      this.peerConnection.close();
      this.peerConnection = null;
    }
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => track.stop());
      this.localStream = null;
    }
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.close();
    }
    this.websocket = null;
    this.remoteStream = null;
    this.connected = false;
    this.workspaceId = null;
    this.roomId = null;
    this.role = null;
    this.participantId = null;
    this.onDisconnectedCallback?.();
    this.emit("disconnected");
  }
  createPeerConnection() {
    const config = {
      iceServers: this.webrtcConfig.iceServers || [
        { urls: "stun:stun.l.google.com:19302" }
      ]
    };
    this.peerConnection = new RTCPeerConnection(config);
    this.peerConnection.onconnectionstatechange = () => {
      const state = this.peerConnection?.connectionState;
      console.info(`\uD83D\uDD0C WebRTC connection state: ${state}`);
    };
    this.peerConnection.oniceconnectionstatechange = () => {
      const state = this.peerConnection?.iceConnectionState;
      console.info(`\uD83E\uDDCA ICE connection state: ${state}`);
    };
    this.peerConnection.onicecandidate = (event) => {
      if (event.candidate && this.workspaceId && this.roomId && this.participantId) {
        this.sendWebRTCSignal(this.workspaceId, this.roomId, this.participantId, {
          type: "ice",
          candidate: event.candidate.toJSON()
        });
      }
    };
    this.peerConnection.ontrack = (event) => {
      console.info("\uD83D\uDCFA Received remote track:", event.track.kind);
      this.remoteStream = event.streams[0] || null;
      this.emit("remoteStream", this.remoteStream);
    };
    return this.peerConnection;
  }
  async createOffer() {
    if (!this.peerConnection) {
      throw new Error("Peer connection not created");
    }
    const offer = await this.peerConnection.createOffer();
    await this.peerConnection.setLocalDescription(offer);
    return offer;
  }
  async createAnswer(offer) {
    if (!this.peerConnection) {
      throw new Error("Peer connection not created");
    }
    await this.peerConnection.setRemoteDescription(offer);
    const answer = await this.peerConnection.createAnswer();
    await this.peerConnection.setLocalDescription(answer);
    return answer;
  }
  async setRemoteDescription(description) {
    if (!this.peerConnection) {
      throw new Error("Peer connection not created");
    }
    await this.peerConnection.setRemoteDescription(description);
  }
  async addIceCandidate(candidate) {
    if (!this.peerConnection) {
      throw new Error("Peer connection not created");
    }
    await this.peerConnection.addIceCandidate(candidate);
  }
  async startProducing(constraints) {
    const mediaConstraints = constraints || this.webrtcConfig.constraints;
    try {
      this.localStream = await navigator.mediaDevices.getUserMedia(mediaConstraints);
      return this.localStream;
    } catch (error) {
      throw new Error(`Failed to start video production: ${error}`);
    }
  }
  async startScreenShare() {
    try {
      this.localStream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          width: this.webrtcConfig.resolution?.width || 1920,
          height: this.webrtcConfig.resolution?.height || 1080,
          frameRate: this.webrtcConfig.framerate || 30
        },
        audio: false
      });
      return this.localStream;
    } catch (error) {
      throw new Error(`Failed to start screen share: ${error}`);
    }
  }
  stopProducing() {
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => track.stop());
      this.localStream = null;
    }
  }
  getLocalStream() {
    return this.localStream;
  }
  getRemoteStream() {
    return this.remoteStream;
  }
  getPeerConnection() {
    return this.peerConnection;
  }
  async getStats() {
    if (!this.peerConnection) {
      return null;
    }
    const stats = await this.peerConnection.getStats();
    return this.extractVideoStats(stats);
  }
  sendJoinMessage() {
    if (!this.websocket || !this.participantId || !this.role)
      return;
    const joinMessage = {
      participant_id: this.participantId,
      role: this.role
    };
    this.websocket.send(JSON.stringify(joinMessage));
  }
  handleMessage(message) {
    switch (message.type) {
      case "joined":
        console.log(`Successfully joined room ${message.room_id} as ${message.role}`);
        break;
      case "heartbeat_ack":
        console.debug("Heartbeat acknowledged");
        break;
      case "error":
        this.handleError(message.message);
        break;
      default:
        this.handleRoleSpecificMessage(message);
    }
  }
  handleRoleSpecificMessage(message) {
    this.emit("message", message);
  }
  handleError(errorMessage) {
    console.error("Video client error:", errorMessage);
    this.onErrorCallback?.(errorMessage);
    this.emit("error", errorMessage);
  }
  async sendHeartbeat() {
    if (!this.connected || !this.websocket)
      return;
    const message = { type: "heartbeat" };
    this.websocket.send(JSON.stringify(message));
  }
  isConnected() {
    return this.connected;
  }
  getConnectionInfo() {
    return {
      connected: this.connected,
      workspace_id: this.workspaceId,
      room_id: this.roomId,
      role: this.role,
      participant_id: this.participantId,
      base_url: this.baseUrl
    };
  }
  onError(callback) {
    this.onErrorCallback = callback;
  }
  onConnected(callback) {
    this.onConnectedCallback = callback;
  }
  onDisconnected(callback) {
    this.onDisconnectedCallback = callback;
  }
  async fetchApi(endpoint, options = {}) {
    const url = `${this.apiBase}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      signal: AbortSignal.timeout(this.options.timeout || 5000)
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }
  extractVideoStats(stats) {
    let inboundVideoStats = null;
    let outboundVideoStats = null;
    stats.forEach((report) => {
      if (report.type === "inbound-rtp" && "kind" in report && report.kind === "video") {
        inboundVideoStats = report;
      } else if (report.type === "outbound-rtp" && "kind" in report && report.kind === "video") {
        outboundVideoStats = report;
      }
    });
    if (inboundVideoStats) {
      return {
        videoBitsPerSecond: inboundVideoStats.bytesReceived || 0,
        framesPerSecond: inboundVideoStats.framesPerSecond || 0,
        frameWidth: inboundVideoStats.frameWidth || 0,
        frameHeight: inboundVideoStats.frameHeight || 0,
        packetsLost: inboundVideoStats.packetsLost || 0,
        totalPackets: inboundVideoStats.packetsReceived || inboundVideoStats.framesDecoded || 0
      };
    }
    if (outboundVideoStats) {
      return {
        videoBitsPerSecond: outboundVideoStats.bytesSent || 0,
        framesPerSecond: outboundVideoStats.framesPerSecond || 0,
        frameWidth: outboundVideoStats.frameWidth || 0,
        frameHeight: outboundVideoStats.frameHeight || 0,
        packetsLost: outboundVideoStats.packetsLost || 0,
        totalPackets: outboundVideoStats.packetsSent || outboundVideoStats.framesSent || 0
      };
    }
    return null;
  }
  generateWorkspaceId() {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === "x" ? r : r & 3 | 8;
      return v.toString(16);
    });
  }
}
// src/video/producer.ts
class VideoProducer extends VideoClientCore {
  consumerConnections = new Map;
  constructor(baseUrl = "http://localhost:8000", options = {}) {
    super(baseUrl, options);
  }
  async connect(workspaceId, roomId, participantId) {
    const success = await this.connectToRoom(workspaceId, roomId, "producer", participantId);
    if (success) {
      this.on("consumer_joined", (consumerId) => {
        console.info(`\uD83C\uDFAF Consumer ${consumerId} joined, initiating WebRTC...`);
        this.initiateWebRTCWithConsumer(consumerId);
      });
      setTimeout(() => this.connectToExistingConsumers(), 1000);
    }
    return success;
  }
  async connectToExistingConsumers() {
    if (!this.workspaceId || !this.roomId)
      return;
    try {
      const roomInfo = await this.getRoomInfo(this.workspaceId, this.roomId);
      for (const consumerId of roomInfo.participants.consumers) {
        if (!this.consumerConnections.has(consumerId)) {
          console.info(`\uD83D\uDD04 Connecting to existing consumer ${consumerId}`);
          await this.initiateWebRTCWithConsumer(consumerId);
        }
      }
    } catch (error) {
      console.error("Failed to connect to existing consumers:", error);
    }
  }
  createPeerConnectionForConsumer(consumerId) {
    const config = {
      iceServers: this.webrtcConfig.iceServers || [
        { urls: "stun:stun.l.google.com:19302" }
      ]
    };
    const peerConnection = new RTCPeerConnection(config);
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => {
        peerConnection.addTrack(track, this.localStream);
      });
    }
    peerConnection.onconnectionstatechange = () => {
      const state = peerConnection.connectionState;
      console.info(`\uD83D\uDD0C WebRTC connection state for ${consumerId}: ${state}`);
      if (state === "failed" || state === "disconnected") {
        console.warn(`Connection to ${consumerId} failed, attempting restart...`);
        setTimeout(() => this.restartConnectionToConsumer(consumerId), 2000);
      }
    };
    peerConnection.oniceconnectionstatechange = () => {
      const state = peerConnection.iceConnectionState;
      console.info(`\uD83E\uDDCA ICE connection state for ${consumerId}: ${state}`);
    };
    peerConnection.onicecandidate = (event) => {
      if (event.candidate && this.workspaceId && this.roomId && this.participantId) {
        this.sendWebRTCSignal(this.workspaceId, this.roomId, this.participantId, {
          type: "ice",
          candidate: event.candidate.toJSON(),
          target_consumer: consumerId
        });
      }
    };
    this.consumerConnections.set(consumerId, peerConnection);
    return peerConnection;
  }
  async restartConnectionToConsumer(consumerId) {
    console.info(`\uD83D\uDD04 Restarting connection to consumer ${consumerId}`);
    await this.initiateWebRTCWithConsumer(consumerId);
  }
  handleConsumerLeft(consumerId) {
    const peerConnection = this.consumerConnections.get(consumerId);
    if (peerConnection) {
      peerConnection.close();
      this.consumerConnections.delete(consumerId);
      console.info(`\uD83E\uDDF9 Cleaned up peer connection for consumer ${consumerId}`);
    }
  }
  async restartConnectionsWithNewStream(stream) {
    console.info("\uD83D\uDD04 Restarting connections with new stream...", { streamId: stream.id });
    for (const [consumerId, peerConnection] of this.consumerConnections) {
      peerConnection.close();
      console.info(`\uD83E\uDDF9 Closed existing connection to consumer ${consumerId}`);
    }
    this.consumerConnections.clear();
    try {
      if (this.workspaceId && this.roomId) {
        const roomInfo = await this.getRoomInfo(this.workspaceId, this.roomId);
        for (const consumerId of roomInfo.participants.consumers) {
          console.info(`\uD83D\uDD04 Creating new connection to consumer ${consumerId}...`);
          await this.initiateWebRTCWithConsumer(consumerId);
        }
      }
    } catch (error) {
      console.error("Failed to restart connections:", error);
    }
  }
  async startCamera(constraints) {
    if (!this.connected) {
      throw new Error("Must be connected to start camera");
    }
    const stream = await this.startProducing(constraints);
    this.localStream = stream;
    await this.restartConnectionsWithNewStream(stream);
    this.notifyStreamStarted(stream);
    return stream;
  }
  async startScreenShare() {
    if (!this.connected) {
      throw new Error("Must be connected to start screen share");
    }
    const stream = await super.startScreenShare();
    this.localStream = stream;
    await this.restartConnectionsWithNewStream(stream);
    this.notifyStreamStarted(stream);
    return stream;
  }
  async stopStreaming() {
    if (!this.connected || !this.websocket) {
      throw new Error("Must be connected to stop streaming");
    }
    for (const [consumerId, peerConnection] of this.consumerConnections) {
      peerConnection.close();
      console.info(`\uD83E\uDDF9 Closed connection to consumer ${consumerId}`);
    }
    this.consumerConnections.clear();
    this.stopProducing();
    this.notifyStreamStopped();
  }
  async updateVideoConfig(config) {
    if (!this.connected || !this.websocket) {
      throw new Error("Must be connected to update video config");
    }
    const message = {
      type: "video_config_update",
      config,
      timestamp: new Date().toISOString()
    };
    this.websocket.send(JSON.stringify(message));
  }
  async sendEmergencyStop(reason = "Emergency stop") {
    if (!this.connected || !this.websocket) {
      throw new Error("Must be connected to send emergency stop");
    }
    const message = {
      type: "emergency_stop",
      reason,
      timestamp: new Date().toISOString()
    };
    this.websocket.send(JSON.stringify(message));
  }
  async initiateWebRTCWithConsumer(consumerId) {
    if (!this.workspaceId || !this.roomId || !this.participantId) {
      console.warn("WebRTC not ready, skipping negotiation with consumer");
      return;
    }
    if (this.consumerConnections.has(consumerId)) {
      const existingConn = this.consumerConnections.get(consumerId);
      existingConn?.close();
      this.consumerConnections.delete(consumerId);
    }
    try {
      console.info(`\uD83D\uDD04 Creating WebRTC offer for consumer ${consumerId}...`);
      const peerConnection = this.createPeerConnectionForConsumer(consumerId);
      const offer = await peerConnection.createOffer();
      await peerConnection.setLocalDescription(offer);
      console.info(`\uD83D\uDCE4 Sending WebRTC offer to consumer ${consumerId}...`);
      await this.sendWebRTCSignal(this.workspaceId, this.roomId, this.participantId, {
        type: "offer",
        sdp: offer.sdp,
        target_consumer: consumerId
      });
      console.info(`\u2705 WebRTC offer sent to consumer ${consumerId}`);
    } catch (error) {
      console.error(`Failed to initiate WebRTC with consumer ${consumerId}:`, error);
    }
  }
  async handleWebRTCAnswer(message) {
    try {
      const consumerId = message.from_consumer;
      console.info(`\uD83D\uDCE5 Received WebRTC answer from consumer ${consumerId}`);
      const peerConnection = this.consumerConnections.get(consumerId);
      if (!peerConnection) {
        console.warn(`No peer connection found for consumer ${consumerId}`);
        return;
      }
      const answer = new RTCSessionDescription({
        type: "answer",
        sdp: message.answer.sdp
      });
      await peerConnection.setRemoteDescription(answer);
      console.info(`\u2705 WebRTC negotiation completed with consumer ${consumerId}`);
    } catch (error) {
      console.error(`Failed to handle WebRTC answer from ${message.from_consumer}:`, error);
      this.handleError(`Failed to handle WebRTC answer: ${error}`);
    }
  }
  async handleWebRTCIce(message) {
    try {
      const consumerId = message.from_consumer;
      if (!consumerId) {
        console.warn("No consumer ID in ICE message");
        return;
      }
      const peerConnection = this.consumerConnections.get(consumerId);
      if (!peerConnection) {
        console.warn(`No peer connection found for consumer ${consumerId}`);
        return;
      }
      console.info(`\uD83D\uDCE5 Received WebRTC ICE from consumer ${consumerId}`);
      const candidate = new RTCIceCandidate(message.candidate);
      await peerConnection.addIceCandidate(candidate);
      console.info(`\u2705 WebRTC ICE handled with consumer ${consumerId}`);
    } catch (error) {
      console.error(`Failed to handle WebRTC ICE from ${message.from_consumer}:`, error);
      this.handleError(`Failed to handle WebRTC ICE: ${error}`);
    }
  }
  handleRoleSpecificMessage(message) {
    switch (message.type) {
      case "participant_joined":
        if (message.role === "consumer" && message.participant_id !== this.participantId) {
          console.info(`\uD83C\uDFAF Consumer ${message.participant_id} joined room`);
          this.emit("consumer_joined", message.participant_id);
        }
        break;
      case "participant_left":
        if (message.role === "consumer") {
          console.info(`\uD83D\uDC4B Consumer ${message.participant_id} left room`);
          this.handleConsumerLeft(message.participant_id);
        }
        break;
      case "webrtc_answer":
        this.handleWebRTCAnswer(message);
        break;
      case "webrtc_ice":
        this.handleWebRTCIce(message);
        break;
      case "status_update":
        this.handleStatusUpdate(message);
        break;
      case "stream_stats":
        this.handleStreamStats(message);
        break;
      case "emergency_stop":
        console.warn(`\uD83D\uDEA8 Emergency stop: ${message.reason || "Unknown reason"}`);
        this.handleError(`Emergency stop: ${message.reason || "Unknown reason"}`);
        break;
      case "error":
        console.error(`Server error: ${message.message}`);
        this.handleError(message.message);
        break;
      default:
        console.warn(`Unknown message type for producer: ${message.type}`);
    }
  }
  handleStatusUpdate(message) {
    console.info(`\uD83D\uDCCA Status update: ${message.status}`, message.data);
    this.emit("statusUpdate", message.status, message.data);
  }
  handleStreamStats(message) {
    console.debug(`\uD83D\uDCC8 Stream stats:`, message.stats);
    this.emit("streamStats", message.stats);
  }
  async notifyStreamStarted(stream) {
    if (!this.websocket)
      return;
    const message = {
      type: "stream_started",
      config: {
        resolution: this.webrtcConfig.resolution,
        framerate: this.webrtcConfig.framerate,
        bitrate: this.webrtcConfig.bitrate
      },
      participant_id: this.participantId,
      timestamp: new Date().toISOString()
    };
    this.websocket.send(JSON.stringify(message));
    this.emit("streamStarted", stream);
  }
  async notifyStreamStopped() {
    if (!this.websocket)
      return;
    const message = {
      type: "stream_stopped",
      participant_id: this.participantId,
      timestamp: new Date().toISOString()
    };
    this.websocket.send(JSON.stringify(message));
    this.emit("streamStopped");
  }
  static async createAndConnect(baseUrl = "http://localhost:8000", workspaceId, roomId, participantId) {
    const producer = new VideoProducer(baseUrl);
    const roomData = await producer.createRoom(workspaceId, roomId);
    const connected = await producer.connect(roomData.workspaceId, roomData.roomId, participantId);
    if (!connected) {
      throw new Error("Failed to connect as video producer");
    }
    return producer;
  }
  get currentRoomId() {
    return this.roomId;
  }
}
// src/video/consumer.ts
class VideoConsumer extends VideoClientCore {
  onFrameUpdateCallback = null;
  onVideoConfigUpdateCallback = null;
  onStreamStartedCallback = null;
  onStreamStoppedCallback = null;
  onRecoveryTriggeredCallback = null;
  onStatusUpdateCallback = null;
  onStreamStatsCallback = null;
  iceCandidateQueue = [];
  hasRemoteDescription = false;
  constructor(baseUrl = "http://localhost:8000", options = {}) {
    super(baseUrl, options);
  }
  async connect(workspaceId, roomId, participantId) {
    const connected = await this.connectToRoom(workspaceId, roomId, "consumer", participantId);
    if (connected) {
      console.info("\uD83D\uDD27 Creating peer connection for consumer...");
      await this.startReceiving();
    }
    return connected;
  }
  async startReceiving() {
    if (!this.connected) {
      throw new Error("Must be connected to start receiving");
    }
    this.hasRemoteDescription = false;
    this.iceCandidateQueue = [];
    this.createPeerConnection();
    if (this.peerConnection) {
      this.peerConnection.ontrack = (event) => {
        console.info("\uD83D\uDCFA Received remote track:", event.track.kind);
        this.remoteStream = event.streams[0] || null;
        this.emit("remoteStream", this.remoteStream);
        this.emit("streamReceived", this.remoteStream);
      };
    }
  }
  async stopReceiving() {
    if (this.peerConnection) {
      this.peerConnection.close();
      this.peerConnection = null;
    }
    this.remoteStream = null;
    this.emit("streamStopped");
  }
  async handleWebRTCOffer(message) {
    try {
      console.info(`\uD83D\uDCE5 Received WebRTC offer from producer ${message.from_producer}`);
      if (!this.peerConnection) {
        console.warn("No peer connection available to handle offer");
        return;
      }
      this.hasRemoteDescription = false;
      this.iceCandidateQueue = [];
      await this.setRemoteDescription(message.offer);
      this.hasRemoteDescription = true;
      await this.processQueuedIceCandidates();
      const answer = await this.createAnswer(message.offer);
      console.info(`\uD83D\uDCE4 Sending WebRTC answer to producer ${message.from_producer}`);
      if (this.workspaceId && this.roomId && this.participantId) {
        await this.sendWebRTCSignal(this.workspaceId, this.roomId, this.participantId, {
          type: "answer",
          sdp: answer.sdp,
          target_producer: message.from_producer
        });
      }
      console.info("\u2705 WebRTC negotiation completed from consumer side");
    } catch (error) {
      console.error("Failed to handle WebRTC offer:", error);
      this.handleError(`Failed to handle WebRTC offer: ${error}`);
    }
  }
  async handleWebRTCIce(message) {
    if (!this.peerConnection) {
      console.warn("No peer connection available to handle ICE");
      return;
    }
    try {
      console.info(`\uD83D\uDCE5 Received WebRTC ICE from producer ${message.from_producer}`);
      const candidate = new RTCIceCandidate(message.candidate);
      if (!this.hasRemoteDescription) {
        console.info(`\uD83D\uDD04 Queuing ICE candidate from ${message.from_producer} (no remote description yet)`);
        this.iceCandidateQueue.push({
          candidate,
          fromProducer: message.from_producer || "unknown"
        });
        return;
      }
      await this.peerConnection.addIceCandidate(candidate);
      console.info(`\u2705 WebRTC ICE handled from producer ${message.from_producer}`);
    } catch (error) {
      console.error(`Failed to handle WebRTC ICE from ${message.from_producer}:`, error);
      this.handleError(`Failed to handle WebRTC ICE: ${error}`);
    }
  }
  async processQueuedIceCandidates() {
    if (this.iceCandidateQueue.length === 0) {
      return;
    }
    console.info(`\uD83D\uDD04 Processing ${this.iceCandidateQueue.length} queued ICE candidates`);
    for (const { candidate, fromProducer } of this.iceCandidateQueue) {
      try {
        if (this.peerConnection) {
          await this.peerConnection.addIceCandidate(candidate);
          console.info(`\u2705 Processed queued ICE candidate from ${fromProducer}`);
        }
      } catch (error) {
        console.error(`Failed to process queued ICE candidate from ${fromProducer}:`, error);
      }
    }
    this.iceCandidateQueue = [];
  }
  createPeerConnection() {
    const config = {
      iceServers: this.webrtcConfig.iceServers || [
        { urls: "stun:stun.l.google.com:19302" }
      ]
    };
    this.peerConnection = new RTCPeerConnection(config);
    this.peerConnection.onconnectionstatechange = () => {
      const state = this.peerConnection?.connectionState;
      console.info(`\uD83D\uDD0C WebRTC connection state: ${state}`);
    };
    this.peerConnection.oniceconnectionstatechange = () => {
      const state = this.peerConnection?.iceConnectionState;
      console.info(`\uD83E\uDDCA ICE connection state: ${state}`);
    };
    this.peerConnection.onicecandidate = (event) => {
      if (event.candidate && this.workspaceId && this.roomId && this.participantId) {
        this.sendIceCandidateToProducer(event.candidate);
      }
    };
    this.peerConnection.ontrack = (event) => {
      console.info("\uD83D\uDCFA Received remote track:", event.track.kind);
      this.remoteStream = event.streams[0] || null;
      this.emit("remoteStream", this.remoteStream);
      this.emit("streamReceived", this.remoteStream);
    };
    return this.peerConnection;
  }
  async sendIceCandidateToProducer(candidate) {
    if (!this.workspaceId || !this.roomId || !this.participantId)
      return;
    try {
      const roomInfo = await this.getRoomInfo(this.workspaceId, this.roomId);
      if (roomInfo.participants.producer) {
        await this.sendWebRTCSignal(this.workspaceId, this.roomId, this.participantId, {
          type: "ice",
          candidate: candidate.toJSON(),
          target_producer: roomInfo.participants.producer
        });
      }
    } catch (error) {
      console.error("Failed to send ICE candidate to producer:", error);
    }
  }
  async handleStreamStarted(message) {
    if (this.onStreamStartedCallback) {
      this.onStreamStartedCallback(message.config, message.participant_id);
    }
    this.emit("streamStarted", message.config, message.participant_id);
    console.info(`\uD83D\uDE80 Stream started by producer ${message.participant_id}, ready to receive video`);
  }
  onFrameUpdate(callback) {
    this.onFrameUpdateCallback = callback;
  }
  onVideoConfigUpdate(callback) {
    this.onVideoConfigUpdateCallback = callback;
  }
  onStreamStarted(callback) {
    this.onStreamStartedCallback = callback;
  }
  onStreamStopped(callback) {
    this.onStreamStoppedCallback = callback;
  }
  onRecoveryTriggered(callback) {
    this.onRecoveryTriggeredCallback = callback;
  }
  onStatusUpdate(callback) {
    this.onStatusUpdateCallback = callback;
  }
  onStreamStats(callback) {
    this.onStreamStatsCallback = callback;
  }
  handleRoleSpecificMessage(message) {
    switch (message.type) {
      case "frame_update":
        this.handleFrameUpdate(message);
        break;
      case "video_config_update":
        this.handleVideoConfigUpdate(message);
        break;
      case "stream_started":
        this.handleStreamStarted(message);
        break;
      case "stream_stopped":
        this.handleStreamStopped(message);
        break;
      case "recovery_triggered":
        this.handleRecoveryTriggered(message);
        break;
      case "status_update":
        this.handleStatusUpdate(message);
        break;
      case "stream_stats":
        this.handleStreamStats(message);
        break;
      case "participant_joined":
        console.info(`\uD83D\uDCE5 Participant joined: ${message.participant_id} as ${message.role}`);
        break;
      case "participant_left":
        console.info(`\uD83D\uDCE4 Participant left: ${message.participant_id} (${message.role})`);
        break;
      case "webrtc_offer":
        this.handleWebRTCOffer(message);
        break;
      case "webrtc_answer":
        console.info("\uD83D\uDCE8 Received WebRTC answer (consumer should not receive this)");
        break;
      case "webrtc_ice":
        this.handleWebRTCIce(message);
        break;
      case "emergency_stop":
        console.warn(`\uD83D\uDEA8 Emergency stop: ${message.reason || "Unknown reason"}`);
        this.handleError(`Emergency stop: ${message.reason || "Unknown reason"}`);
        break;
      case "error":
        console.error(`Server error: ${message.message}`);
        this.handleError(message.message);
        break;
      default:
        console.warn(`Unknown message type for consumer: ${message.type}`);
    }
  }
  handleFrameUpdate(message) {
    if (this.onFrameUpdateCallback) {
      const frameData = {
        data: message.data,
        metadata: message.metadata
      };
      this.onFrameUpdateCallback(frameData);
    }
    this.emit("frameUpdate", message.data);
  }
  handleVideoConfigUpdate(message) {
    if (this.onVideoConfigUpdateCallback) {
      this.onVideoConfigUpdateCallback(message.config);
    }
    this.emit("videoConfigUpdate", message.config);
  }
  handleStreamStopped(message) {
    if (this.onStreamStoppedCallback) {
      this.onStreamStoppedCallback(message.participant_id, message.reason);
    }
    this.emit("streamStopped", message.participant_id, message.reason);
  }
  handleRecoveryTriggered(message) {
    if (this.onRecoveryTriggeredCallback) {
      this.onRecoveryTriggeredCallback(message.policy, message.reason);
    }
    this.emit("recoveryTriggered", message.policy, message.reason);
  }
  handleStatusUpdate(message) {
    if (this.onStatusUpdateCallback) {
      this.onStatusUpdateCallback(message.status, message.data);
    }
    this.emit("statusUpdate", message.status, message.data);
  }
  handleStreamStats(message) {
    if (this.onStreamStatsCallback) {
      this.onStreamStatsCallback(message.stats);
    }
    this.emit("streamStats", message.stats);
  }
  static async createAndConnect(workspaceId, roomId, baseUrl = "http://localhost:8000", participantId) {
    const consumer = new VideoConsumer(baseUrl);
    const connected = await consumer.connect(workspaceId, roomId, participantId);
    if (!connected) {
      throw new Error("Failed to connect as video consumer");
    }
    return consumer;
  }
  attachToVideoElement(videoElement) {
    if (this.remoteStream) {
      videoElement.srcObject = this.remoteStream;
    }
    this.on("remoteStream", (stream) => {
      videoElement.srcObject = stream;
    });
  }
  async getVideoStats() {
    const stats = await this.getStats();
    return stats;
  }
}
// src/video/factory.ts
function createClient2(role, baseUrl = "http://localhost:8000", options = {}) {
  if (role === "producer") {
    return new VideoProducer(baseUrl, options);
  }
  if (role === "consumer") {
    return new VideoConsumer(baseUrl, options);
  }
  throw new Error(`Invalid role: ${role}. Must be 'producer' or 'consumer'`);
}
async function createProducerClient2(baseUrl = "http://localhost:8000", workspaceId, roomId, participantId, options = {}) {
  const producer = new VideoProducer(baseUrl, options);
  const roomData = await producer.createRoom(workspaceId, roomId);
  const connected = await producer.connect(roomData.workspaceId, roomData.roomId, participantId);
  if (!connected) {
    throw new Error("Failed to connect as video producer");
  }
  return producer;
}
async function createConsumerClient2(workspaceId, roomId, baseUrl = "http://localhost:8000", participantId, options = {}) {
  const consumer = new VideoConsumer(baseUrl, options);
  const connected = await consumer.connect(workspaceId, roomId, participantId);
  if (!connected) {
    throw new Error("Failed to connect as video consumer");
  }
  return consumer;
}
// src/index.ts
var VERSION = "1.0.0";
export {
  exports_video as video,
  exports_robotics as robotics,
  VERSION
};

//# debugId=4A2D211384B624B064756E2164756E21
//# sourceMappingURL=index.js.map
