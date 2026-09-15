"""Mock tools — return per-scenario data. Signature stays tool-like; swap for real MCP later."""
def slack_thread(data: dict) -> str:   return data.get("slack", "(no chatter)")
def fetch_logs(data: dict) -> str:     return data.get("logs", "(no logs)")
def recent_deploys(data: dict) -> str: return data.get("deploys", "(no recent deploys)")
def search_incidents(data: dict) -> str: return data.get("incidents", "(no related incidents)")
def create_ticket(draft: dict) -> str: return f"[MOCK] Created JIRA INC-999 sev={draft.get('severity')} owner={draft.get('owner')}"
def post_slack(msg) -> str:            return f"[MOCK] Posted to #incidents: {msg}"
