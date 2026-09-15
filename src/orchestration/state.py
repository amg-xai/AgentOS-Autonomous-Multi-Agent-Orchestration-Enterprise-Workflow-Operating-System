import operator
from typing import Annotated, TypedDict

class IncidentState(TypedDict, total=False):
    incident_id: str
    alert: str
    data: dict                 # per-scenario tool data (slack/logs/deploys/incidents)
    plan: str
    comms_summary: str
    log_findings: str
    deploy_correlation: str
    related_incidents: str
    draft: dict
    verification: str
    approved: bool
    result: str
    trace: Annotated[list, operator.add]
