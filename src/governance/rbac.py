"""Minimal role-based access control. High-impact actions require the right permission."""
ROLES={
    "viewer":   {"view"},
    "operator": {"view", "approve_low_impact"},
    "admin":    {"view", "approve_low_impact", "approve_high_impact", "configure"},
}
def can(role, permission):
    return permission in ROLES.get(role, set())
def permissions(role):
    return sorted(ROLES.get(role, set()))
