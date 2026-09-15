import json, re
from src.tools import mock_tools as T
from src.llm import call_llm

def run_baseline(alert: str, data: dict, incident_id: str = "incident-001") -> dict:
    context = (
        f"Alert: {alert}\n\nSlack thread:\n{T.slack_thread(data)}\n\n"
        f"Logs:\n{T.fetch_logs(data)}\n\nRecent deploys:\n{T.recent_deploys(data)}\n\n"
        f"Past incidents:\n{T.search_incidents(data)}"
    )
    raw = call_llm(
        "You are a SINGLE incident-response agent. Read everything and SYNTHESIZE a draft incident record. "
        "Respond ONLY as JSON, no markdown, no code fences. Keys and allowed values: "
        "severity (SEV-1 = >25% errors or full outage; SEV-2 = 5-25% errors, partial; SEV-3 = <5%, minor), "
        "owner (one of: payments-team, platform-team, frontend-team, unassigned), "
        "root_cause_hypothesis (string), recommended_action (string).",
        context,
    )
    return {"incident_id": incident_id, "system": "baseline", "draft": _parse(raw)}

def _parse(raw):
    s = raw.strip()
    s = re.sub(r"^```(json)?", "", s).strip(); s = re.sub(r"```$", "", s).strip()
    try: return json.loads(s)
    except Exception:
        m = re.search(r"\{.*\}", s, re.DOTALL)
        if m:
            try: return json.loads(m.group(0))
            except Exception: pass
    return {"severity": "UNKNOWN", "owner": "unassigned",
            "root_cause_hypothesis": raw[:200], "recommended_action": "manual review"}
