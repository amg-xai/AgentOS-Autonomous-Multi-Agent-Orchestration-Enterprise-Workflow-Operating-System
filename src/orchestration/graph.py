from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.orchestration.state import IncidentState
from src.agents.agents import (supervisor, comms_reader, log_analyzer,
    deploy_correlator, duplicate_finder, synthesizer, verifier, execute_action)

def build_graph():
    g = StateGraph(IncidentState)
    for name, fn in [("supervisor", supervisor), ("comms_reader", comms_reader),
                     ("log_analyzer", log_analyzer), ("deploy_correlator", deploy_correlator),
                     ("duplicate_finder", duplicate_finder), ("synthesizer", synthesizer),
                     ("verifier", verifier), ("execute_action", execute_action)]:
        g.add_node(name, fn)
    g.add_edge(START, "supervisor")
    g.add_edge("supervisor", "comms_reader")
    g.add_edge("comms_reader", "log_analyzer")
    g.add_edge("log_analyzer", "deploy_correlator")
    g.add_edge("deploy_correlator", "duplicate_finder")
    g.add_edge("duplicate_finder", "synthesizer")
    g.add_edge("synthesizer", "verifier")
    g.add_edge("verifier", "execute_action")
    g.add_edge("execute_action", END)
    return g.compile(checkpointer=MemorySaver(), interrupt_before=["execute_action"])