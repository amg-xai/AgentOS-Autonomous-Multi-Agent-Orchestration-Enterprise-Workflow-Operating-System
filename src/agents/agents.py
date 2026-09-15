import json
from src.tools import mock_tools as T
from src.llm import call_llm

def supervisor(state):
    plan = call_llm("You are the SUPERVISOR agent for incident response. Make a short investigation plan.",
                    f"Alert: {state['alert']}")
    return {"plan": plan, "trace": [{"node": "supervisor", "out": plan}]}

def comms_reader(state):
    out = call_llm("You are the SLACK/COMMS agent. Summarize the incident discussion.",
                   T.slack_thread(state.get("data", {})))
    return {"comms_summary": out, "trace": [{"node": "comms_reader", "out": out}]}

def log_analyzer(state):
    out = call_llm("You are the LOG analyzer agent. Report the key error signal and the error rate.",
                   T.fetch_logs(state.get("data", {})))
    return {"log_findings": out, "trace": [{"node": "log_analyzer", "out": out}]}

def deploy_correlator(state):
    out = call_llm("You are the DEPLOY correlator agent (GitHub). Identify which recent deploy most likely "
                   "caused this incident, matching timing and the affected component.",
                   T.recent_deploys(state.get("data", {})))
    return {"deploy_correlation": out, "trace": [{"node": "deploy_correlator", "out": out}]}

def duplicate_finder(state):
    out = call_llm("You are the JIRA duplicate-finder agent. Find related past incidents.",
                   T.search_incidents(state.get("data", {})))
    return {"related_incidents": out, "trace": [{"node": "duplicate_finder", "out": out}]}

def synthesizer(state):
    ctx = (f"Alert: {state['alert']}\nComms: {state.get('comms_summary')}\n"
           f"Logs: {state.get('log_findings')}\nDeploys: {state.get('deploy_correlation')}\n"
           f"Related: {state.get('related_incidents')}")
    raw = call_llm("You SYNTHESIZE a draft incident record. Respond ONLY as JSON, no markdown, no code fences. "
                   "Keys and allowed values: "
                   "severity (SEV-1 = >25% errors or full outage; SEV-2 = 5-25% errors, partial; SEV-3 = <5%, minor), "
                   "owner (one of: payments-team, platform-team, frontend-team, unassigned), "
                   "root_cause_hypothesis (string), recommended_action (string).", ctx)
    draft = _parse(raw)
    return {"draft": draft, "trace": [{"node": "synthesizer", "out": draft}]}

def verifier(state):
    out = call_llm("You are the VERIFIER agent. Check the draft is consistent with the evidence and safe. "
                   "If the owner or severity looks wrong given the data, say so.",
                   json.dumps(state.get("draft", {})))
    return {"verification": out, "trace": [{"node": "verifier", "out": out}]}

def execute_action(state):
    draft = state.get("draft", {})
    result = f"{T.create_ticket(draft)} | {T.post_slack(draft.get('recommended_action', ''))}"
    return {"approved": True, "result": result, "trace": [{"node": "execute_action", "out": result}]}

def _parse(raw):
    """Robust JSON parse: strips ```json fences and grabs the first {...} block."""
    import re
    s = raw.strip()
    s = re.sub(r"^```(json)?", "", s).strip()
    s = re.sub(r"```$", "", s).strip()
    try:
        return json.loads(s)
    except Exception:
        m = re.search(r"\{.*\}", s, re.DOTALL)
        if m:
            try: return json.loads(m.group(0))
            except Exception: pass
    return {"severity": "UNKNOWN", "owner": "unassigned",
            "root_cause_hypothesis": raw[:200], "recommended_action": "manual review"}
