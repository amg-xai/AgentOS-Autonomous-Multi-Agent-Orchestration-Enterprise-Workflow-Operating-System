import time
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.orchestration.state import IncidentState
from src.agents.agents import (supervisor, comms_reader, log_analyzer,
    deploy_correlator, duplicate_finder, synthesizer, verifier, execute_action)
from src.observability.trace import record_span
from src.governance.audit import log as audit_log

def _instrument(name, fn):
    """Wrap a node so every execution emits a correlated trace span + audit entry."""
    def wrapped(state):
        rid = state.get("incident_id", "unknown")
        t0 = time.time(); result = fn(state); dt = time.time() - t0
        summ = ""
        if isinstance(result, dict) and result.get("trace"):
            summ = result["trace"][-1].get("out", "")
        record_span(rid, name, dt, summ)
        audit_log(rid, actor=f"agent:{name}", action="node_executed", detail=summ)
        return result
    return wrapped

def build_graph(use_verifier=True, use_memory=True, use_specialists=True, instrument=False):
    g = StateGraph(IncidentState)
    nodes = {"supervisor": supervisor, "synthesizer": synthesizer, "execute_action": execute_action,
             "comms_reader": comms_reader, "log_analyzer": log_analyzer,
             "deploy_correlator": deploy_correlator, "duplicate_finder": duplicate_finder,
             "verifier": verifier}
    def add(name):
        fn = nodes[name]
        g.add_node(name, _instrument(name, fn) if instrument else fn)

    add("supervisor"); add("synthesizer"); add("execute_action")
    seq = ["supervisor"]
    if use_specialists:
        for n in ["comms_reader", "log_analyzer", "deploy_correlator"]:
            add(n); seq.append(n)
        if use_memory:
            add("duplicate_finder"); seq.append("duplicate_finder")
    seq.append("synthesizer")
    if use_verifier:
        add("verifier"); seq.append("verifier")
    seq.append("execute_action")

    g.add_edge(START, seq[0])
    for a, b in zip(seq, seq[1:]):
        g.add_edge(a, b)
    g.add_edge("execute_action", END)
    return g.compile(checkpointer=MemorySaver(), interrupt_before=["execute_action"])
