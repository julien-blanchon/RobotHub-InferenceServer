export declare const CreateSessionRequestSchema: {
    readonly properties: {
        readonly session_id: {
            readonly type: "string";
            readonly title: "Session Id";
        };
        readonly policy_path: {
            readonly type: "string";
            readonly title: "Policy Path";
        };
        readonly camera_names: {
            readonly items: {
                readonly type: "string";
            };
            readonly type: "array";
            readonly title: "Camera Names";
            readonly default: readonly ["front"];
        };
        readonly arena_server_url: {
            readonly type: "string";
            readonly title: "Arena Server Url";
            readonly default: "http://localhost:8000";
        };
        readonly workspace_id: {
            readonly anyOf: readonly [{
                readonly type: "string";
            }, {
                readonly type: "null";
            }];
            readonly title: "Workspace Id";
        };
        readonly policy_type: {
            readonly type: "string";
            readonly title: "Policy Type";
            readonly default: "act";
        };
        readonly language_instruction: {
            readonly anyOf: readonly [{
                readonly type: "string";
            }, {
                readonly type: "null";
            }];
            readonly title: "Language Instruction";
        };
    };
    readonly type: "object";
    readonly required: readonly ["session_id", "policy_path"];
    readonly title: "CreateSessionRequest";
};
export declare const CreateSessionResponseSchema: {
    readonly properties: {
        readonly workspace_id: {
            readonly type: "string";
            readonly title: "Workspace Id";
        };
        readonly camera_room_ids: {
            readonly additionalProperties: {
                readonly type: "string";
            };
            readonly type: "object";
            readonly title: "Camera Room Ids";
        };
        readonly joint_input_room_id: {
            readonly type: "string";
            readonly title: "Joint Input Room Id";
        };
        readonly joint_output_room_id: {
            readonly type: "string";
            readonly title: "Joint Output Room Id";
        };
    };
    readonly type: "object";
    readonly required: readonly ["workspace_id", "camera_room_ids", "joint_input_room_id", "joint_output_room_id"];
    readonly title: "CreateSessionResponse";
};
export declare const HTTPValidationErrorSchema: {
    readonly properties: {
        readonly detail: {
            readonly items: {
                readonly $ref: "#/components/schemas/ValidationError";
            };
            readonly type: "array";
            readonly title: "Detail";
        };
    };
    readonly type: "object";
    readonly title: "HTTPValidationError";
};
export declare const SessionStatusResponseSchema: {
    readonly properties: {
        readonly session_id: {
            readonly type: "string";
            readonly title: "Session Id";
        };
        readonly status: {
            readonly type: "string";
            readonly title: "Status";
        };
        readonly policy_path: {
            readonly type: "string";
            readonly title: "Policy Path";
        };
        readonly policy_type: {
            readonly type: "string";
            readonly title: "Policy Type";
        };
        readonly camera_names: {
            readonly items: {
                readonly type: "string";
            };
            readonly type: "array";
            readonly title: "Camera Names";
        };
        readonly workspace_id: {
            readonly type: "string";
            readonly title: "Workspace Id";
        };
        readonly rooms: {
            readonly additionalProperties: true;
            readonly type: "object";
            readonly title: "Rooms";
        };
        readonly stats: {
            readonly additionalProperties: true;
            readonly type: "object";
            readonly title: "Stats";
        };
        readonly inference_stats: {
            readonly anyOf: readonly [{
                readonly additionalProperties: true;
                readonly type: "object";
            }, {
                readonly type: "null";
            }];
            readonly title: "Inference Stats";
        };
        readonly error_message: {
            readonly anyOf: readonly [{
                readonly type: "string";
            }, {
                readonly type: "null";
            }];
            readonly title: "Error Message";
        };
    };
    readonly type: "object";
    readonly required: readonly ["session_id", "status", "policy_path", "policy_type", "camera_names", "workspace_id", "rooms", "stats"];
    readonly title: "SessionStatusResponse";
};
export declare const ValidationErrorSchema: {
    readonly properties: {
        readonly loc: {
            readonly items: {
                readonly anyOf: readonly [{
                    readonly type: "string";
                }, {
                    readonly type: "integer";
                }];
            };
            readonly type: "array";
            readonly title: "Location";
        };
        readonly msg: {
            readonly type: "string";
            readonly title: "Message";
        };
        readonly type: {
            readonly type: "string";
            readonly title: "Error Type";
        };
    };
    readonly type: "object";
    readonly required: readonly ["loc", "msg", "type"];
    readonly title: "ValidationError";
};
//# sourceMappingURL=schemas.gen.d.ts.map