from src.agents.baseline import run_baseline

def main():
    alert = "Monitoring: checkout 500 error rate 12% since 14:20"
    print("=== BASELINE: single agent + tools (no orchestration) ===\n")
    out = run_baseline(alert)
    print("Draft:", out["draft"])
    print("\n(Note: no supervisor, no specialists, no verifier, no approval gate.)")

if __name__ == "__main__":
    main()