import json
from src.orchestration.graph import build_graph
from src.governance import rbac, audit

CURRENT_USER = "alice"
CURRENT_ROLE = "admin"     # try "operator" to see RBAC block the high-impact action

def main():
    scenarios = json.load(open("scenarios/incidents.json"))
    sc = scenarios[0]
    graph = build_graph(instrument=True)   # tracing + audit ON for live runs
    config = {"configurable": {"thread_id": sc["id"]}}
    initial = {"incident_id": sc["id"], "alert": sc["alert"], "data": sc["data"], "trace": []}

    print(f"User: {CURRENT_USER} (role={CURRENT_ROLE}, permissions={rbac.permissions(CURRENT_ROLE)})")
    print(f"=== INVESTIGATING: {sc['alert']} ===\n")
    audit.log(sc["id"], actor=f"user:{CURRENT_USER}", action="run_started", detail=sc["alert"])

    state = graph.invoke(initial, config)
    for t in state["trace"]:
        print(f"[{t['node']}] -> {t['out']}\n")
    print("=== PROPOSED (high-impact: create Jira ticket) ===")
    print("Draft:", state["draft"])

    if not rbac.can(CURRENT_ROLE, "approve_high_impact"):
        audit.log(sc["id"], actor=f"user:{CURRENT_USER}", action="approval_denied_rbac",
                  detail=f"role {CURRENT_ROLE} lacks approve_high_impact")
        print(f"\n[RBAC] Role '{CURRENT_ROLE}' is not permitted to approve high-impact actions. Blocked.")
        return

    decision = input("\nApprove creating this ticket? (y/n): ").strip().lower()
    if decision == "y":
        audit.log(sc["id"], actor=f"user:{CURRENT_USER}", action="approval_granted", detail="create ticket")
        final = graph.invoke(None, config)
        audit.log(sc["id"], actor=f"user:{CURRENT_USER}", action="action_executed", detail=final["result"])
        print("\n=== EXECUTED ===\n" + final["result"])
    else:
        audit.log(sc["id"], actor=f"user:{CURRENT_USER}", action="approval_rejected", detail="no action")
        print("\nRejected. No action taken.")
    print("\n(Audit trail -> logs/audit.jsonl , traces -> logs/traces.jsonl)")

if __name__ == "__main__":
    main()