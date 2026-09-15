from src.orchestration.graph import build_graph

def main():
    graph = build_graph()
    config = {"configurable": {"thread_id": "incident-001"}}
    initial = {"incident_id": "incident-001",
               "alert": "Monitoring: checkout 500 error rate 12% since 14:20", "trace": []}

    print("=== RUNNING INVESTIGATION (pauses before any action) ===\n")
    state = graph.invoke(initial, config)
    for t in state["trace"]:
        print(f"[{t['node']}] -> {t['out']}\n")

    print("=== PROPOSED (needs human approval) ===")
    print("Draft:", state["draft"])
    print("Verifier:", state["verification"])

    if input("\nApprove this action? (y/n): ").strip().lower() == "y":
        final = graph.invoke(None, config)
        print("\n=== EXECUTED ===\n" + final["result"])
    else:
        print("\nRejected. No action taken. (Trace still recorded.)")

if __name__ == "__main__":
    main()