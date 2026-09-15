import json, time
from src.agents.baseline import run_baseline
from src.orchestration.graph import build_graph

def run_full(alert, data, incident_id):
    graph = build_graph()
    config = {"configurable": {"thread_id": incident_id}}
    state = graph.invoke({"incident_id": incident_id, "alert": alert, "data": data, "trace": []}, config)
    return state.get("draft", {}), len(state.get("trace", []))

def score(draft, expected):
    return sum(1 for k, v in expected.items()
               if str(draft.get(k, "")).strip().lower() == str(v).strip().lower()), len(expected)

def main():
    scenarios = json.load(open("scenarios/incidents.json"))
    print(f"{'scenario':<22}{'system':<10}{'accuracy':<10}{'steps':<7}{'sec':<6}")
    print("-" * 58)
    tot = {"baseline": [0, 0], "full": [0, 0]}
    for sc in scenarios:
        t0 = time.time(); b = run_baseline(sc["alert"], sc["data"], sc["id"]); bt = time.time() - t0
        bh, bn = score(b["draft"], sc["expected"]); tot["baseline"][0]+=bh; tot["baseline"][1]+=bn
        print(f"{sc['id']:<22}{'baseline':<10}{f'{bh}/{bn}':<10}{'1':<7}{bt:<6.1f}")
        t0 = time.time(); fd, fs = run_full(sc["alert"], sc["data"], sc["id"]); ft = time.time() - t0
        fh, fn = score(fd, sc["expected"]); tot["full"][0]+=fh; tot["full"][1]+=fn
        print(f"{sc['id']:<22}{'full':<10}{f'{fh}/{fn}':<10}{fs:<7}{ft:<6.1f}\n")
    print("=== TOTALS ===")
    for s,(h,n) in tot.items(): print(f"{s:<10} accuracy {h}/{n}  ({100*h/n:.0f}%)")

if __name__ == "__main__":
    main()
