import json
from src.orchestration.graph import build_graph

def main():
    scenarios = json.load(open("scenarios/incidents.json"))
    sc = scenarios[0]   # demo with the first scenario
    graph = build_graph()
    config = {"configurable": {"thread_id": sc["id"]}}
    initial = {"incident_id": sc["id"], "alert": sc["alert"], "data": sc["data"], "trace": []}
    print(f"=== INVESTIGATING: {sc['alert']} ===\n")
    state = graph.invoke(initial, config)
    for t in state["trace"]:
        print(f"[{t['node']}] -> {t['out']}\n")
    print("=== PROPOSED ===\nDraft:", state["draft"])
    if input("\nApprove? (y/n): ").strip().lower() == "y":
        print("\n=== EXECUTED ===\n" + graph.invoke(None, config)["result"])
    else:
        print("\nRejected. No action taken.")

if __name__ == "__main__":
    main()
