"""Single-agent baseline: ONE agent, same tools, no supervisor/specialists/verifier.
This is the control condition we compare the full multi-agent system against."""
import json
from src.tools import mock_tools as T
from src.llm import call_llm   # swap for src.llm later

def run_baseline(alert: str, incident_id: str = "incident-001") -> dict:
    context = (
        f"Alert: {alert}\n\n"
        f"Slack thread:\n{T.slack_thread(incident_id)}\n\n"
        f"Logs:\n{T.fetch_logs()}\n\n"
        f"Recent deploys:\n{T.recent_deploys()}\n\n"
        f"Past incidents:\n{T.search_incidents()}"
    )
    raw = call_llm("You SYNTHESIZE a draft incident record. Respond ONLY as JSON, no markdown, no code fences. "
                   "Keys and allowed values: "
                   "severity (one of: SEV-1, SEV-2, SEV-3), "
                   "owner (one of: payments-team, platform-team, frontend-team, unassigned), "
                   "root_cause_hypothesis (string), "
                   "recommended_action (string).", context)
    try:
        draft = json.loads(raw)
    except Exception:
        draft = {"severity": "UNKNOWN", "owner": "unassigned",
                 "root_cause_hypothesis": raw, "recommended_action": "manual review"}
    return {"incident_id": incident_id, "system": "baseline", "draft": draft}