def slack_thread(incident_id: str) -> str:
    return ("[#incidents] 14:22 @user: checkout throwing 500s\n"
            "14:23 @oncall: looking\n14:25 @user2: ~1 in 8 requests")
def fetch_logs(service: str = "payment-service") -> str:
    return "14:18 ERROR NullPointerException at CheckoutHandler.process()\nerror_rate=12% window=5m"
def recent_deploys(service: str = "payment-service") -> str:
    return "14:15 payment-service v2.3.1 by @dev (PR #412: refactor checkout handler)"
def search_incidents(query: str = "checkout 500") -> str:
    return "INC-204: checkout 500s after payment deploy (resolved by rollback)"
def create_ticket(draft: dict) -> str:
    return f"[MOCK] Created JIRA INC-205 sev={draft.get('severity')} owner={draft.get('owner')}"
def post_slack(msg: str) -> str:
    return f"[MOCK] Posted to #incidents: {msg}"