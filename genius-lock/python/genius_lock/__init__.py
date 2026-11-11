"""Genius Lock client: collision-free locks for AI agents.

Every request gets a clear answer: the resource is yours, or a clean conflict.
No dependencies beyond the Python standard library.
"""
import json
import urllib.error
import urllib.parse
import urllib.request
from contextlib import contextmanager

__version__ = "0.1.0"
DEFAULT_BASE_URL = "https://dfn-investor-desk.ignacio-89b.workers.dev"


class GeniusLockError(Exception):
    """Any error returned by the service (invalid key, limits, bad request)."""


class Conflict(GeniusLockError):
    """Another holder already has the resource. Nothing was allocated twice."""

    def __init__(self, body):
        super().__init__(body.get("message", "Conflict: the resource is already held."))
        self.body = body
        self.resource = body.get("resource")
        self.held_until = body.get("held_until")
        self.collision_number = body.get("collision_number")


class GeniusLock:
    def __init__(self, key, base_url=DEFAULT_BASE_URL, timeout=10):
        if not key:
            raise ValueError("A Genius Lock key is required (free at https://datafarmnet.com/investors/lock.html)")
        self.key = key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _call(self, method, path, payload=None):
        url = self.base_url + path
        data = None
        if method == "GET" and payload:
            url += "?" + urllib.parse.urlencode(payload)
        elif payload is not None:
            data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, method=method, headers={
            "Authorization": "Bearer " + self.key,
            "content-type": "application/json",
            "user-agent": "genius-lock-python/" + __version__,
        })
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return r.status, json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            try:
                body = json.loads(e.read().decode() or "{}")
            except ValueError:
                body = {"error": str(e)}
            return e.code, body

    def acquire(self, resource, holder, ttl_seconds=300):
        """Try to take the resource. Returns the response dict; raises Conflict if someone else has it."""
        status, body = self._call("POST", "/lock/v1/acquire", {"resource": resource, "holder": holder, "ttl_seconds": ttl_seconds})
        if status == 409:
            raise Conflict(body)
        if status >= 400:
            raise GeniusLockError(body.get("error", "HTTP %s" % status))
        return body

    def release(self, resource, holder):
        status, body = self._call("POST", "/lock/v1/release", {"resource": resource, "holder": holder})
        if status >= 400:
            raise GeniusLockError(body.get("error", "HTTP %s" % status))
        return body

    def status(self, resource):
        status, body = self._call("GET", "/lock/v1/status", {"resource": resource})
        if status >= 400:
            raise GeniusLockError(body.get("error", "HTTP %s" % status))
        return body

    @contextmanager
    def hold(self, resource, holder, ttl_seconds=300):
        """Hold a resource for the duration of a with-block; released automatically."""
        self.acquire(resource, holder, ttl_seconds)
        try:
            yield
        finally:
            try:
                self.release(resource, holder)
            except GeniusLockError:
                pass


__all__ = ["GeniusLock", "Conflict", "GeniusLockError"]
