import json
def call_llm(system: str, user: str) -> str:
    s = system.lower()
    if "supervisor" in s:
        return "1) read Slack thread 2) analyze logs 3) check recent deploys 4) search past incidents"
    if "slack" in s or "comms" in s:
        return "Users report 500 errors on checkout since ~14:20. On-call acknowledged."
    if "log" in s:
        return "Spike in NullPointerException in payment-service after 14:18; error rate 12%."
    if "deploy" in s:
        return "payment-service v2.3.1 deployed at 14:15 by @dev; changed the checkout handler."
    if "jira" in s or "duplicate" in s:
        return "INC-204 (3 months ago) had similar checkout 500s after a payment deploy."
    if "synthesize" in s or "draft" in s:
        return json.dumps({
            "severity": "SEV-2",
            "owner": "payments-team",
            "root_cause_hypothesis": "Regression in checkout handler from v2.3.1 deploy at 14:15.",
            "recommended_action": "Roll back payment-service to v2.3.0 and open incident ticket."
        })
    if "verif" in s:
        return "Consistent: deploy time precedes error spike; severity matches error rate. OK."
    return "ok"