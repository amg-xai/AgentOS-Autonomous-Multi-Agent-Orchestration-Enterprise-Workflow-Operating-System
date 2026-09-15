from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.orchestration.state import IncidentState
from src.agents.agents import (supervisor, comms_reader, log_analyzer,
    deploy_correlator, duplicate_finder, synthesizer, verifier, execute_action)

def build_graph(use_verifier: bool = True, use_memory: bool = True,
                use_specialists: bool = True):
    g = StateGraph(IncidentState)
    g.add_node("supervisor", supervisor)
    g.add_node("synthesizer", synthesizer)
    g.add_node("execute_action", execute_action)

    seq = ["supervisor"]
    if use_specialists:
        g.add_node("comms_reader", comms_reader)
        g.add_node("log_analyzer", log_analyzer)
        g.add_node("deploy_correlator", deploy_correlator)
        seq += ["comms_reader", "log_analyzer", "deploy_correlator"]
        if use_memory:
            g.add_node("duplicate_finder", duplicate_finder)
            seq.append("duplicate_finder")
    seq.append("synthesizer")
    if use_verifier:
        g.add_node("verifier", verifier)
        seq.append("verifier")
    seq.append("execute_action")

    g.add_edge(START, seq[0])
    for a, b in zip(seq, seq[1:]):
        g.add_edge(a, b)
    g.add_edge("execute_action", END)
    return g.compile(checkpointer=MemorySaver(), interrupt_before=["execute_action"])