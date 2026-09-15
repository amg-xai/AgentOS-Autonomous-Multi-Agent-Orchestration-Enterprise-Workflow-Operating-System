import json
from src.tools import mock_tools as T
from src.llm_stub import call_llm

def supervisor(state):
    plan = call_llm("You are the SUPERVISOR agent for incident response. Make a short investigation plan.",
                    f"Alert: {state['alert']}")
    return {"plan": plan, "trace": [{"node": "supervisor", "out": plan}]}

def comms_reader(state):
    out = call_llm("You are the SLACK/COMMS agent. Summarize the incident discussion.",
                   T.slack_thread(state["incident_id"]))
    return {"comms_summary": out, "trace": [{"node": "comms_reader", "out": out}]}

def log_analyzer(state):
    out = call_llm("You are the LOG analyzer agent. Report the key error signal.", T.fetch_logs())
    return {"log_findings": out, "trace": [{"node": "log_analyzer", "out": out}]}

def deploy_correlator(state):
    out = call_llm("You are the DEPLOY correlator agent (GitHub). Link recent deploys to the incident.",
                   T.recent_deploys())
    return {"deploy_correlation": out, "trace": [{"node": "deploy_correlator", "out": out}]}

def duplicate_finder(state):
    out = call_llm("You are the JIRA duplicate-finder agent. Find related past incidents.",
                   T.search_incidents())
    return {"related_incidents": out, "trace": [{"node": "duplicate_finder", "out": out}]}

def synthesizer(state):
    ctx = (f"Alert: {state['alert']}\nComms: {state.get('comms_summary')}\n"
           f"Logs: {state.get('log_findings')}\nDeploys: {state.get('deploy_correlation')}\n"
           f"Related: {state.get('related_incidents')}")
    raw = call_llm("You SYNTHESIZE a draft incident record. Respond ONLY as JSON with keys: "
                   "severity, owner, root_cause_hypothesis, recommended_action.", ctx)
    try:
        draft = json.loads(raw)
    except Exception:
        draft = {"severity": "UNKNOWN", "owner": "unassigned",
                 "root_cause_hypothesis": raw, "recommended_action": "manual review"}
    return {"draft": draft, "trace": [{"node": "synthesizer", "out": draft}]}

def verifier(state):
    out = call_llm("You are the VERIFIER agent. Check the draft is consistent and safe. Note any problems.",
                   json.dumps(state.get("draft", {})))
    return {"verification": out, "trace": [{"node": "verifier", "out": out}]}

def execute_action(state):
    draft = state.get("draft", {})
    result = f"{T.create_ticket(draft)} | {T.post_slack(draft.get('recommended_action', ''))}"
    return {"approved": True, "result": result, "trace": [{"node": "execute_action", "out": result}]}