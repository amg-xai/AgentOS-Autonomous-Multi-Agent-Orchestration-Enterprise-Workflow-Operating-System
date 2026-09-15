"""Run BOTH systems on every scenario and score them. This produces the comparison."""
import json, time
from src.agents.baseline import run_baseline
from src.orchestration.graph import build_graph

def run_full(alert, incident_id):
    graph = build_graph()
    config = {"configurable": {"thread_id": incident_id}}
    state = graph.invoke({"incident_id": incident_id, "alert": alert, "trace": []}, config)
    return state.get("draft", {}), len(state.get("trace", []))

def score(draft, expected):
    hits = sum(1 for k, v in expected.items()
               if str(draft.get(k, "")).lower() == str(v).lower())
    return hits, len(expected)

def main():
    scenarios = json.load(open("scenarios/incidents.json"))
    print(f"{'scenario':<14}{'system':<10}{'accuracy':<10}{'steps':<7}{'sec':<6}")
    print("-" * 50)
    totals = {"baseline": [0, 0], "full": [0, 0]}
    for sc in scenarios:
        t0 = time.time(); b = run_baseline(sc["alert"], sc["id"]); bt = time.time() - t0
        bh, bn = score(b["draft"], sc["expected"])
        totals["baseline"][0] += bh; totals["baseline"][1] += bn
        print(f"{sc['id']:<14}{'baseline':<10}{f'{bh}/{bn}':<10}{'1':<7}{bt:<6.2f}")

        t0 = time.time(); fdraft, fsteps = run_full(sc["alert"], sc["id"]); ft = time.time() - t0
        fh, fn = score(fdraft, sc["expected"])
        totals["full"][0] += fh; totals["full"][1] += fn
        print(f"{sc['id']:<14}{'full':<10}{f'{fh}/{fn}':<10}{fsteps:<7}{ft:<6.2f}")
        print()
    print("=== TOTALS ===")
    for sys_, (h, n) in totals.items():
        print(f"{sys_:<10} accuracy {h}/{n}  ({100*h/n:.0f}%)")

if __name__ == "__main__":
    main()

    