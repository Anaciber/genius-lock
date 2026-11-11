"""Two agents ask for the same restaurant table at the same instant. Only one gets it.

Usage: GENIUS_LOCK_KEY=gl_... python examples/two_agents.py
"""
import os
import sys
import threading
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))
from genius_lock import GeniusLock, Conflict  # noqa: E402

lock = GeniusLock(os.environ["GENIUS_LOCK_KEY"])
table = "table-12:friday-21h:" + uuid.uuid4().hex[:6]
barrier = threading.Barrier(2)


def agent(name):
    barrier.wait()
    try:
        lock.acquire(table, holder=name, ttl_seconds=60)
        print(f"{name}: it's mine!")
    except Conflict as c:
        print(f"{name}: conflict, already taken (collision #{c.collision_number} prevented). Looking for another.")


threads = [threading.Thread(target=agent, args=(n,)) for n in ("agent-A", "agent-B")]
[t.start() for t in threads]
[t.join() for t in threads]
