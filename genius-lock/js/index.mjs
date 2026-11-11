// Genius Lock client: collision-free locks for AI agents.
// Every request gets a clear answer: the resource is yours, or a clean conflict.
export const DEFAULT_BASE_URL = "https://dfn-investor-desk.ignacio-89b.workers.dev";

export class Conflict extends Error {
  constructor(body) {
    super(body.message || "Conflict: the resource is already held.");
    this.name = "Conflict";
    this.body = body;
    this.collisionNumber = body.collision_number;
    this.heldUntil = body.held_until;
  }
}

export class GeniusLock {
  constructor(key, baseUrl = DEFAULT_BASE_URL) {
    if (!key) throw new Error("A Genius Lock key is required (free at https://datafarmnet.com/investors/lock.html)");
    this.key = key;
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async #call(method, path, payload) {
    let url = this.baseUrl + path;
    const init = { method, headers: { Authorization: "Bearer " + this.key, "content-type": "application/json" } };
    if (method === "GET" && payload) url += "?" + new URLSearchParams(payload);
    else if (payload) init.body = JSON.stringify(payload);
    const res = await fetch(url, init);
    const body = await res.json().catch(() => ({}));
    return { status: res.status, body };
  }

  /** Try to take the resource. Returns { ok: true, ... } or { ok: false, conflict: true, ... }. */
  async acquire(resource, holder, ttlSeconds = 300) {
    const { status, body } = await this.#call("POST", "/lock/v1/acquire", { resource, holder, ttl_seconds: ttlSeconds });
    if (status >= 400 && status !== 409) throw new Error(body.error || `HTTP ${status}`);
    return body;
  }

  async release(resource, holder) {
    const { status, body } = await this.#call("POST", "/lock/v1/release", { resource, holder });
    if (status >= 400) throw new Error(body.error || `HTTP ${status}`);
    return body;
  }

  async status(resource) {
    const { status, body } = await this.#call("GET", "/lock/v1/status", { resource });
    if (status >= 400) throw new Error(body.error || `HTTP ${status}`);
    return body;
  }

  /** Run fn only if the resource is acquired; always releases. Throws Conflict otherwise. */
  async hold(resource, holder, fn, ttlSeconds = 300) {
    const r = await this.acquire(resource, holder, ttlSeconds);
    if (!r.ok) throw new Conflict(r);
    try { return await fn(); } finally { await this.release(resource, holder).catch(() => {}); }
  }
}
