"""FastAPI layer: exposes the incident-response graph over HTTP.
Run:  uvicorn src.api.server:app --reload --port 8000
"""
import os, json, uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.orchestration.graph import build_graph
from src.governance import rbac, audit

app = FastAPI(title="AgentOS Incident Response API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_RUNS = {}

class IncidentIn(BaseModel):
    alert: str
    slack: str = ""
    logs: str = ""
    deploys: str = ""
    user: str = "alice"
    role: str = "admin"

class Decision(BaseModel):
    user: str = "alice"
    role: str = "admin"

@app.post("/incidents")
def submit_incident(inc: IncidentIn):
    rid = "inc-" + uuid.uuid4().hex[:8]
    graph = build_graph(instrument=True)
    config = {"configurable": {"thread_id": rid}}
    data = {"slack": inc.slack, "logs": inc.logs, "deploys": inc.deploys, "incidents": ""}
    audit.log(rid, actor=f"user:{inc.user}", action="run_started", detail=inc.alert)
    state = graph.invoke({"incident_id": rid, "alert": inc.alert, "data": data, "trace": []}, config)
    _RUNS[rid] = {"graph": graph, "config": config}
    return {"run_id": rid, "draft": state.get("draft", {}),
            "trace": state.get("trace", []), "awaiting_approval": True}

@app.post("/incidents/{rid}/approve")
def approve(rid: str, d: Decision):
    if rid not in _RUNS:
        raise HTTPException(404, "unknown run_id")
    if not rbac.can(d.role, "approve_high_impact"):
        audit.log(rid, actor=f"user:{d.user}", action="approval_denied_rbac",
                  detail=f"role {d.role} lacks approve_high_impact")
        raise HTTPException(403, f"role '{d.role}' cannot approve high-impact actions")
    audit.log(rid, actor=f"user:{d.user}", action="approval_granted", detail="create ticket")
    final = _RUNS[rid]["graph"].invoke(None, _RUNS[rid]["config"])
    audit.log(rid, actor=f"user:{d.user}", action="action_executed", detail=final["result"])
    return {"run_id": rid, "result": final["result"], "executed": True}

@app.post("/incidents/{rid}/reject")
def reject(rid: str, d: Decision):
    if rid not in _RUNS:
        raise HTTPException(404, "unknown run_id")
    audit.log(rid, actor=f"user:{d.user}", action="approval_rejected", detail="no action")
    return {"run_id": rid, "executed": False}

@app.get("/audit")
def get_audit(limit: int = 100):
    path = os.path.join("logs", "audit.jsonl")
    if not os.path.exists(path):
        return {"entries": []}
    lines = open(path, encoding="utf-8").read().strip().splitlines()
    return {"entries": [json.loads(l) for l in lines[-limit:]]}

@app.get("/results")
def get_results():
    path = os.path.join("results", "ablation.json")
    if os.path.exists(path):
        return json.load(open(path))
    return {"note": "no results file", "rows": []}

@app.get("/")
def root():
    return {"service": "AgentOS Incident Response API",
            "endpoints": ["/incidents", "/incidents/{id}/approve", "/incidents/{id}/reject", "/audit", "/results"]}