# Genius Lock

**Your AI agents will never get the same thing twice.**

When several AI agents act at once on something that exists only once (a calendar slot, the last unit in stock, a file, a task), one of them silently overwrites the other: a double booking, an oversold item, a lost update. Genius Lock gives every request a clear answer: **yours**, or a **clean conflict**.

- Works with any MCP-compatible agent (Claude, ChatGPT and others) or from your code (REST, Python, JavaScript).
- Atomic: if two agents ask for the same resource in the same instant, exactly one gets it.
- Holds expire automatically (default 5 minutes, max 24 hours), so no agent can keep a resource forever.
- Free: 10,000 operations a month.

See it in ten seconds: https://datafarmnet.com/investors/race-en.html

## 1. Get a free key

https://datafarmnet.com/investors/lock.html (email only, instant).

## 2a. Use it from an agent (MCP)

Add this remote MCP server to your agent:

```
https://dfn-investor-desk.ignacio-89b.workers.dev/lock/mcp?k=YOUR_KEY
```

Tools: `acquire_resource`, `release_resource`, `resource_status`.

## 2b. Use it from code

### Python

```bash
pip install "git+https://github.com/anaciber/genius-lock.git#subdirectory=python"
```

```python
from genius_lock import GeniusLock, Conflict

lock = GeniusLock("YOUR_KEY")

try:
    with lock.hold("calendar:dr-lopez:2026-11-20T10:00", holder="agent-7", ttl_seconds=300):
        book_the_slot()          # only one agent ever gets here for this slot
except Conflict as c:
    pick_another_slot()          # c.collision_number tells you which collision was prevented
```

### JavaScript

```js
import { GeniusLock, Conflict } from "./js/index.mjs";

const lock = new GeniusLock("YOUR_KEY");
const r = await lock.acquire("stock:sku-123:last-unit", "agent-B");
if (r.ok) { /* sell it */ await lock.release("stock:sku-123:last-unit", "agent-B"); }
else { /* conflict: someone else has it */ }
```

### REST

```bash
curl -X POST https://dfn-investor-desk.ignacio-89b.workers.dev/lock/v1/acquire \
  -H "Authorization: Bearer YOUR_KEY" -H "content-type: application/json" \
  -d '{"resource":"table-12:fri-21h","holder":"agent-A","ttl_seconds":300}'
# 200 {"ok":true,...}   409 {"ok":false,"conflict":true,"collision_number":...}
```

Endpoints: `POST /lock/v1/acquire`, `POST /lock/v1/release`, `GET /lock/v1/status?resource=...`

## Rules for your agents

1. Acquire before acting on anything your agents share.
2. Treat a conflict as "not yours": pick something else, never retry blindly.
3. Release when done (or let the hold expire).
4. Do not put personal data in resource or holder names.

## Free and paid

| | Genius Lock (free) | Genius City (paid) |
|---|---|---|
| Scope | Your own agents | Resources shared across organisations |
| Guarantee | Atomic allocation in software | Allocation verified in hardware (Pranaxis, FPGA on AMD) |
| Extras | | Verifiable registry, proof of every commitment, multi-party settlement |

Genius City: https://datafarmnet.com

## Why this exists

Read [The Last Seat](https://datafarmnet.com/investors/the-last-seat.html), a five-minute story about an AI agent that logged 4,112 collisions before it found a better way. Live counter of collisions prevented: https://datafarmnet.com/investors/live.html

## License

Client libraries and examples in this repository: MIT. The Genius Lock service is provided by Data Farm Network, S.L. (Badajoz, Spain) under its terms of use: https://datafarmnet.com/investors/lock.html
