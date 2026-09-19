// Central API client — points at the FastAPI backend.
const BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function submitIncident(payload) {
  const r = await fetch(`${BASE}/incidents`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`submit failed (${r.status})`);
  return r.json();
}
export async function approve(runId, who) {
  const r = await fetch(`${BASE}/incidents/${runId}/approve`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(who),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || `approve failed (${r.status})`);
  return data;
}
export async function reject(runId, who) {
  const r = await fetch(`${BASE}/incidents/${runId}/reject`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(who),
  });
  return r.json();
}
export async function getAudit() {
  const r = await fetch(`${BASE}/audit`); return r.json();
}
export async function getResults() {
  const r = await fetch(`${BASE}/results`); return r.json();
}
