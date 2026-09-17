"""Lightweight tracing: one correlated span per node execution, written to logs/traces.jsonl."""
import os, json
from datetime import datetime, timezone
_DIR="logs"; os.makedirs(_DIR, exist_ok=True)
_FILE=os.path.join(_DIR,"traces.jsonl")

def record_span(run_id, node, duration_s, output_summary=""):
    entry={"ts":datetime.now(timezone.utc).isoformat(),"run_id":run_id,"node":node,
           "duration_s":round(duration_s,3),"output":str(output_summary)[:200]}
    with open(_FILE,"a",encoding="utf-8") as f:
        f.write(json.dumps(entry)+"\n")
    return entry
