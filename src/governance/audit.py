"""Append-only audit log of agent decisions, tool calls, and approvals -> logs/audit.jsonl."""
import os, json
from datetime import datetime, timezone
_DIR="logs"; os.makedirs(_DIR, exist_ok=True)
_FILE=os.path.join(_DIR,"audit.jsonl")

def log(run_id, actor, action, detail=""):
    entry={"ts":datetime.now(timezone.utc).isoformat(),"run_id":run_id,
           "actor":actor,"action":action,"detail":str(detail)[:300]}
    with open(_FILE,"a",encoding="utf-8") as f:
        f.write(json.dumps(entry)+"\n")
    return entry
