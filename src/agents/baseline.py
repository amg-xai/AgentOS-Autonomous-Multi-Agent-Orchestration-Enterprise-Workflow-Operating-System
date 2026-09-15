"""Single-agent baseline: ONE agent, same tools, no supervisor/specialists/verifier.
This is the control condition we compare the full multi-agent system against."""
import json
from src.tools import mock_tools as T
from src.llm_stub import call_llm   # swap for src.llm later

def run_baseline(alert: str, incident_id: str = "incident-001") -> dict:
    context = (
        f"Alert: {alert}\n\n"
        f"Slack thread:\n{T.slack_thread(incident_id)}\n\n"
        f"Logs:\n{T.fetch_logs()}\n\n"
        f"Recent deploys:\n{T.recent_deploys()}\n\n"
        f"Past incidents:\n{T.search_incidents()}"
    )
    raw = call_llm(
        "You are a SINGLE incident-response agent. Read everything and SYNTHESIZE a draft "
        "incident record. Respond ONLY as JSON with keys: severity, owner, "
        "root_cause_hypothesis, recommended_action.",
        context,
    )
    try:
        draft = json.loads(raw)
    except Exception:
        draft = {"severity": "UNKNOWN", "owner": "unassigned",
                 "root_cause_hypothesis": raw, "recommended_action": "manual review"}
    return {"incident_id": incident_id, "system": "baseline", "draft": draft}