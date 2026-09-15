"""Ablation: run the full system with each component turned off, measure the change.
Answers O5 — which components actually contribute to accuracy?"""
import json, time
from src.agents.baseline import run_baseline
from src.orchestration.graph import build_graph

VARIANTS = {
    "baseline (1 agent)":      None,  # special-cased below
    "full":                    dict(use_verifier=True,  use_memory=True,  use_specialists=True),
    "no_verifier":             dict(use_verifier=False, use_memory=True,  use_specialists=True),
    "no_memory":               dict(use_verifier=True,  use_memory=False, use_specialists=True),
    "no_specialists":          dict(use_verifier=True,  use_memory=True,  use_specialists=False),
}

def score(draft, expected):
    return sum(1 for k, v in expected.items()
               if str(draft.get(k, "")).strip().lower() == str(v).strip().lower()), len(expected)

def run_variant(cfg, alert, data, iid):
    graph = build_graph(**cfg)
    state = graph.invoke({"incident_id": iid, "alert": alert, "data": data, "trace": []},
                         {"configurable": {"thread_id": iid + str(cfg)}})
    return state.get("draft", {}), len(state.get("trace", []))

def main():
    scenarios = json.load(open("scenarios/incidents.json"))
    print(f"{'variant':<20}{'accuracy':<12}{'avg_steps':<11}{'avg_sec':<8}")
    print("-" * 51)
    for name, cfg in VARIANTS.items():
        hits = tot = steps_sum = 0; t0 = time.time()
        for sc in scenarios:
            if cfg is None:
                d = run_baseline(sc["alert"], sc["data"], sc["id"])["draft"]; steps = 1
            else:
                d, steps = run_variant(cfg, sc["alert"], sc["data"], sc["id"])
            h, n = score(d, sc["expected"]); hits += h; tot += n; steps_sum += steps
        secs = (time.time() - t0) / len(scenarios)
        print(f"{name:<20}{f'{hits}/{tot} ({100*hits/tot:.0f}%)':<12}"
              f"{steps_sum/len(scenarios):<11.1f}{secs:<8.1f}")

if __name__ == "__main__":
    main()
