// @bun
// src/schemas.gen.ts
var CreateSessionRequestSchema = {
  properties: {
    session_id: {
      type: "string",
      title: "Session Id"
    },
    policy_path: {
      type: "string",
      title: "Policy Path"
    },
    transport_server_url: {
      type: "string",
      title: "Transport Server Url"
    },
    camera_names: {
      items: {
        type: "string"
      },
      type: "array",
      title: "Camera Names",
      default: ["front"]
    },
    workspace_id: {
      anyOf: [
        {
          type: "string"
        },
        {
          type: "null"
        }
      ],
      title: "Workspace Id"
    },
    policy_type: {
      type: "string",
      title: "Policy Type",
      default: "act"
    },
    language_instruction: {
      anyOf: [
        {
          type: "string"
        },
        {
          type: "null"
        }
      ],
      title: "Language Instruction"
    }
  },
  type: "object",
  required: ["session_id", "policy_path", "transport_server_url"],
  title: "CreateSessionRequest"
};
var CreateSessionResponseSchema = {
  properties: {
    workspace_id: {
      type: "string",
      title: "Workspace Id"
    },
    camera_room_ids: {
      additionalProperties: {
        type: "string"
      },
      type: "object",
      title: "Camera Room Ids"
    },
    joint_input_room_id: {
      type: "string",
      title: "Joint Input Room Id"
    },
    joint_output_room_id: {
      type: "string",
      title: "Joint Output Room Id"
    }
  },
  type: "object",
  required: ["workspace_id", "camera_room_ids", "joint_input_room_id", "joint_output_room_id"],
  title: "CreateSessionResponse"
};
var HTTPValidationErrorSchema = {
  properties: {
    detail: {
      items: {
        $ref: "#/components/schemas/ValidationError"
      },
      type: "array",
      title: "Detail"
    }
  },
  type: "object",
  title: "HTTPValidationError"
};
var SessionStatusResponseSchema = {
  properties: {
    session_id: {
      type: "string",
      title: "Session Id"
    },
    status: {
      type: "string",
      title: "Status"
    },
    policy_path: {
      type: "string",
      title: "Policy Path"
    },
    policy_type: {
      type: "string",
      title: "Policy Type"
    },
    camera_names: {
      items: {
        type: "string"
      },
      type: "array",
      title: "Camera Names"
    },
    workspace_id: {
      type: "string",
      title: "Workspace Id"
    },
    rooms: {
      additionalProperties: true,
      type: "object",
      title: "Rooms"
    },
    stats: {
      additionalProperties: true,
      type: "object",
      title: "Stats"
    },
    inference_stats: {
      anyOf: [
        {
          additionalProperties: true,
          type: "object"
        },
        {
          type: "null"
        }
      ],
      title: "Inference Stats"
    },
    error_message: {
      anyOf: [
        {
          type: "string"
        },
        {
          type: "null"
        }
      ],
      title: "Error Message"
    }
  },
  type: "object",
  required: ["session_id", "status", "policy_path", "policy_type", "camera_names", "workspace_id", "rooms", "stats"],
  title: "SessionStatusResponse"
};
var ValidationErrorSchema = {
  properties: {
    loc: {
      items: {
        anyOf: [
          {
            type: "string"
          },
          {
            type: "integer"
          }
        ]
      },
      type: "array",
      title: "Location"
    },
    msg: {
      type: "string",
      title: "Message"
    },
    type: {
      type: "string",
      title: "Error Type"
    }
  },
  type: "object",
  required: ["loc", "msg", "type"],
  title: "ValidationError"
};
// node_modules/@hey-api/client-fetch/dist/node/index.mjs
var e = /\{[^{}]+\}/g;
var t = ({ allowReserved: e2, name: t2, value: r }) => {
  if (r == null)
    return "";
  if (typeof r == "object")
    throw new Error("Deeply-nested arrays/objects aren\u2019t supported. Provide your own `querySerializer()` to handle these.");
  return `${t2}=${e2 ? r : encodeURIComponent(r)}`;
};
var r = ({ allowReserved: e2, explode: r2, name: s, style: a, value: n }) => {
  if (!r2) {
    const t2 = (e2 ? n : n.map((e3) => encodeURIComponent(e3))).join(((e3) => {
      switch (e3) {
        case "form":
        default:
          return ",";
        case "pipeDelimited":
          return "|";
        case "spaceDelimited":
          return "%20";
      }
    })(a));
    switch (a) {
      case "label":
        return `.${t2}`;
      case "matrix":
        return `;${s}=${t2}`;
      case "simple":
        return t2;
      default:
        return `${s}=${t2}`;
    }
  }
  const o = ((e3) => {
    switch (e3) {
      case "label":
        return ".";
      case "matrix":
        return ";";
      case "simple":
        return ",";
      default:
        return "&";
    }
  })(a), l = n.map((r3) => a === "label" || a === "simple" ? e2 ? r3 : encodeURIComponent(r3) : t({ allowReserved: e2, name: s, value: r3 })).join(o);
  return a === "label" || a === "matrix" ? o + l : l;
};
var s = ({ allowReserved: e2, explode: r2, name: s2, style: a, value: n }) => {
  if (n instanceof Date)
    return `${s2}=${n.toISOString()}`;
  if (a !== "deepObject" && !r2) {
    let t2 = [];
    Object.entries(n).forEach(([r4, s3]) => {
      t2 = [...t2, r4, e2 ? s3 : encodeURIComponent(s3)];
    });
    const r3 = t2.join(",");
    switch (a) {
      case "form":
        return `${s2}=${r3}`;
      case "label":
        return `.${r3}`;
      case "matrix":
        return `;${s2}=${r3}`;
      default:
        return r3;
    }
  }
  const o = ((e3) => {
    switch (e3) {
      case "label":
        return ".";
      case "matrix":
        return ";";
      case "simple":
        return ",";
      default:
        return "&";
    }
  })(a), l = Object.entries(n).map(([r3, n2]) => t({ allowReserved: e2, name: a === "deepObject" ? `${s2}[${r3}]` : r3, value: n2 })).join(o);
  return a === "label" || a === "matrix" ? o + l : l;
};
var a = ({ allowReserved: e2, array: a2, object: n } = {}) => (o) => {
  let l = [];
  if (o && typeof o == "object")
    for (const i in o) {
      const c = o[i];
      c != null && (l = Array.isArray(c) ? [...l, r({ allowReserved: e2, explode: true, name: i, style: "form", value: c, ...a2 })] : typeof c != "object" ? [...l, t({ allowReserved: e2, name: i, value: c })] : [...l, s({ allowReserved: e2, explode: true, name: i, style: "deepObject", value: c, ...n })]);
    }
  return l.join("&");
};
var n = ({ baseUrl: a2, path: n2, query: o, querySerializer: l, url: i }) => {
  let c = a2 + (i.startsWith("/") ? i : `/${i}`);
  n2 && (c = (({ path: a3, url: n3 }) => {
    let o2 = n3;
    const l2 = n3.match(e);
    if (l2)
      for (const e2 of l2) {
        let n4 = false, l3 = e2.substring(1, e2.length - 1), i2 = "simple";
        l3.endsWith("*") && (n4 = true, l3 = l3.substring(0, l3.length - 1)), l3.startsWith(".") ? (l3 = l3.substring(1), i2 = "label") : l3.startsWith(";") && (l3 = l3.substring(1), i2 = "matrix");
        const c2 = a3[l3];
        c2 != null && (o2 = Array.isArray(c2) ? o2.replace(e2, r({ explode: n4, name: l3, style: i2, value: c2 })) : typeof c2 != "object" ? i2 !== "matrix" ? o2.replace(e2, i2 === "label" ? `.${c2}` : c2) : o2.replace(e2, `;${t({ name: l3, value: c2 })}`) : o2.replace(e2, s({ explode: n4, name: l3, style: i2, value: c2 })));
      }
    return o2;
  })({ path: n2, url: c }));
  let u = o ? l(o) : "";
  return u.startsWith("?") && (u = u.substring(1)), u && (c += `?${u}`), c;
};
var o = (e2, t2) => {
  const r2 = { ...e2, ...t2 };
  return r2.baseUrl?.endsWith("/") && (r2.baseUrl = r2.baseUrl.substring(0, r2.baseUrl.length - 1)), r2.headers = l(e2.headers, t2.headers), r2;
};
var l = (...e2) => {
  const t2 = new Headers;
  for (const r2 of e2) {
    if (!r2 || typeof r2 != "object")
      continue;
    const e3 = r2 instanceof Headers ? r2.entries() : Object.entries(r2);
    for (const [r3, s2] of e3)
      if (s2 === null)
        t2.delete(r3);
      else if (Array.isArray(s2))
        for (const e4 of s2)
          t2.append(r3, e4);
      else
        s2 !== undefined && t2.set(r3, typeof s2 == "object" ? JSON.stringify(s2) : s2);
  }
  return t2;
};

class i {
  _fns;
  constructor() {
    this._fns = [];
  }
  eject(e2) {
    const t2 = this._fns.indexOf(e2);
    t2 !== -1 && (this._fns = [...this._fns.slice(0, t2), ...this._fns.slice(t2 + 1)]);
  }
  use(e2) {
    this._fns = [...this._fns, e2];
  }
}
var d = { bodySerializer: (e2) => JSON.stringify(e2) };
var h = a({ allowReserved: false, array: { explode: true, style: "form" }, object: { explode: true, style: "deepObject" } });
var y = { "Content-Type": "application/json" };
var m = (e2 = {}) => ({ ...d, baseUrl: "", fetch: globalThis.fetch, headers: y, parseAs: "auto", querySerializer: h, ...e2 });
var b = (e2 = {}) => {
  let t2 = o(m(), e2);
  const r2 = () => ({ ...t2 }), s2 = { request: new i, response: new i }, c = async (e3) => {
    const r3 = { ...t2, ...e3, headers: l(t2.headers, e3.headers) };
    r3.body && r3.bodySerializer && (r3.body = r3.bodySerializer(r3.body)), r3.body || r3.headers.delete("Content-Type");
    const o2 = n({ baseUrl: r3.baseUrl ?? "", path: r3.path, query: r3.query, querySerializer: typeof r3.querySerializer == "function" ? r3.querySerializer : a(r3.querySerializer), url: r3.url }), i2 = { redirect: "follow", ...r3 };
    let c2 = new Request(o2, i2);
    for (const e4 of s2.request._fns)
      c2 = await e4(c2, r3);
    const u = r3.fetch;
    let d2 = await u(c2);
    for (const e4 of s2.response._fns)
      d2 = await e4(d2, c2, r3);
    const p = { request: c2, response: d2 };
    if (d2.ok) {
      if (d2.status === 204 || d2.headers.get("Content-Length") === "0")
        return { data: {}, ...p };
      if (r3.parseAs === "stream")
        return { data: d2.body, ...p };
      const e4 = (r3.parseAs === "auto" ? ((e5) => {
        if (e5)
          return e5.startsWith("application/json") || e5.endsWith("+json") ? "json" : e5 === "multipart/form-data" ? "formData" : ["application/", "audio/", "image/", "video/"].some((t4) => e5.startsWith(t4)) ? "blob" : e5.startsWith("text/") ? "text" : undefined;
      })(d2.headers.get("Content-Type")) : r3.parseAs) ?? "json";
      let t3 = await d2[e4]();
      return e4 === "json" && r3.responseTransformer && (t3 = await r3.responseTransformer(t3)), { data: t3, ...p };
    }
    let f = await d2.text();
    if (r3.throwOnError)
      throw new Error(f);
    try {
      f = JSON.parse(f);
    } catch {}
    return { error: f || {}, ...p };
  };
  return { connect: (e3) => c({ ...e3, method: "CONNECT" }), delete: (e3) => c({ ...e3, method: "DELETE" }), get: (e3) => c({ ...e3, method: "GET" }), getConfig: r2, head: (e3) => c({ ...e3, method: "HEAD" }), interceptors: s2, options: (e3) => c({ ...e3, method: "OPTIONS" }), patch: (e3) => c({ ...e3, method: "PATCH" }), post: (e3) => c({ ...e3, method: "POST" }), put: (e3) => c({ ...e3, method: "PUT" }), request: c, setConfig: (e3) => (t2 = o(t2, e3), r2()), trace: (e3) => c({ ...e3, method: "TRACE" }) };
};

// src/services.gen.ts
var client = b(m());
var rootGet = (options) => {
  return (options?.client ?? client).get({
    ...options,
    url: "/"
  });
};
var healthCheckHealthGet = (options) => {
  return (options?.client ?? client).get({
    ...options,
    url: "/health"
  });
};
var listSessionsSessionsGet = (options) => {
  return (options?.client ?? client).get({
    ...options,
    url: "/sessions"
  });
};
var createSessionSessionsPost = (options) => {
  return (options?.client ?? client).post({
    ...options,
    url: "/sessions"
  });
};
var startInferenceSessionsSessionIdStartPost = (options) => {
  return (options?.client ?? client).post({
    ...options,
    url: "/sessions/{session_id}/start"
  });
};
var stopInferenceSessionsSessionIdStopPost = (options) => {
  return (options?.client ?? client).post({
    ...options,
    url: "/sessions/{session_id}/stop"
  });
};
var restartInferenceSessionsSessionIdRestartPost = (options) => {
  return (options?.client ?? client).post({
    ...options,
    url: "/sessions/{session_id}/restart"
  });
};
var deleteSessionSessionsSessionIdDelete = (options) => {
  return (options?.client ?? client).delete({
    ...options,
    url: "/sessions/{session_id}"
  });
};
export {
  stopInferenceSessionsSessionIdStopPost,
  startInferenceSessionsSessionIdStartPost,
  rootGet,
  restartInferenceSessionsSessionIdRestartPost,
  listSessionsSessionsGet,
  healthCheckHealthGet,
  deleteSessionSessionsSessionIdDelete,
  createSessionSessionsPost,
  client,
  ValidationErrorSchema,
  SessionStatusResponseSchema,
  HTTPValidationErrorSchema,
  CreateSessionResponseSchema,
  CreateSessionRequestSchema
};

//# debugId=9EA46170B85C82C664756E2164756E21
//# sourceMappingURL=index.js.map
