import { useState, useEffect } from "react";
import { submitIncident, approve, reject, getAudit, getResults } from "./api";

const SEV = { "SEV-1": "sev1", "SEV-2": "sev2", "SEV-3": "sev3" };

function Console() {
  const [form, setForm] = useState({
    alert: "checkout 500 error rate 12% since 14:20",
    slack: "users report 500s on checkout",
    logs: "NullPointerException at CheckoutHandler.process() error_rate=12%",
    deploys: "payment-service v2.3.1 (refactor checkout handler)",
    role: "admin",
  });
  const [run, setRun] = useState(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState(null);
  const [err, setErr] = useState(null);

  const up = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function onSubmit() {
    setBusy(true); setErr(null); setMsg(null); setRun(null);
    try { setRun(await submitIncident(form)); }
    catch (e) { setErr(e.message); }
    finally { setBusy(false); }
  }
  async function onApprove() {
    setBusy(true); setErr(null); setMsg(null);
    try { const r = await approve(run.run_id, { user: "aditya", role: form.role });
      setMsg(r.result); setRun({ ...run, awaiting_approval: false }); }
    catch (e) { setErr(e.message); }
    finally { setBusy(false); }
  }
  async function onReject() {
    setBusy(true); setErr(null);
    try { await reject(run.run_id, { user: "aditya", role: form.role });
      setMsg("Rejected — no action taken."); setRun({ ...run, awaiting_approval: false }); }
    catch (e) { setErr(e.message); }
    finally { setBusy(false); }
  }

  const d = run?.draft || {};
  return (
    <>
      <div className="panel">
        <h2>Report an incident</h2>
        <label>Alert</label>
        <input value={form.alert} onChange={up("alert")} />
        <div className="row">
          <div><label>Slack thread</label><textarea value={form.slack} onChange={up("slack")} /></div>
          <div><label>Logs</label><textarea value={form.logs} onChange={up("logs")} /></div>
        </div>
        <div className="row">
          <div><label>Recent deploys</label><textarea value={form.deploys} onChange={up("deploys")} /></div>
          <div><label>Approver role (RBAC)</label>
            <select value={form.role} onChange={up("role")}>
              <option value="admin">admin (can approve high-impact)</option>
              <option value="operator">operator (cannot)</option>
              <option value="viewer">viewer (cannot)</option>
            </select>
          </div>
        </div>
        <div className="btn-row">
          <button className="btn-blue" onClick={onSubmit} disabled={busy}>
            {busy ? "Investigating…" : "Run investigation"}
          </button>
        </div>
      </div>

      {run && (
        <div className="panel">
          <h2>Proposed triage <span className="pill">run {run.run_id}</span></h2>
          <div className="draft">
            <div className="kv"><span className="k">Severity</span>
              <span className={`badge ${SEV[d.severity] || ""}`}>{d.severity || "—"}</span></div>
            <div className="kv"><span className="k">Owner</span><span>{d.owner || "—"}</span></div>
            <div className="kv"><span className="k">Root cause</span><span>{d.root_cause_hypothesis || "—"}</span></div>
            <div className="kv"><span className="k">Recommended action</span><span>{d.recommended_action || "—"}</span></div>
          </div>

          {run.awaiting_approval && (
            <div className="btn-row">
              <button className="btn-green" onClick={onApprove} disabled={busy}>Approve &amp; create ticket</button>
              <button className="btn-red" onClick={onReject} disabled={busy}>Reject</button>
            </div>
          )}
          {msg && <div className="result-ok">{msg}</div>}
          {err && <div className="result-err">{err}</div>}

          <details style={{ marginTop: 16 }}>
            <summary className="muted" style={{ cursor: "pointer" }}>Agent investigation trace ({run.trace?.length || 0} steps)</summary>
            {run.trace?.map((t, i) => (
              <div className="trace-item" key={i}>
                <span className="trace-node">{t.node}</span>
                <span className="trace-out">{typeof t.out === "string" ? t.out : JSON.stringify(t.out)}</span>
              </div>
            ))}
          </details>
        </div>
      )}
      {err && !run && <div className="panel"><div className="result-err">{err}</div></div>}
    </>
  );
}

function Dashboard() {
  const [data, setData] = useState(null);
  const [err, setErr] = useState(null);
  useEffect(() => { getResults().then(setData).catch((e) => setErr(e.message)); }, []);
  const colors = { "baseline (1 agent)": "var(--blue)", full: "var(--green)",
    no_verifier: "var(--purple)", no_memory: "var(--amber)", no_specialists: "var(--red)" };
  if (err) return <div className="panel"><div className="result-err">API not reachable: {err}</div></div>;
  if (!data) return <div className="panel"><p className="muted">Loading…</p></div>;
  return (
    <div className="panel">
      <h2>Ablation results <span className="pill">{data.benchmark}</span></h2>
      <p className="muted">Model: {data.model} — accuracy by configuration (each component toggled off)</p>
      {data.rows?.map((r) => (
        <div className="bar-wrap" key={r.config}>
          <div className="bar-label">{r.config}</div>
          <div className="bar-track">
            <div className="bar-fill" style={{ width: `${r.accuracy_pct}%`, background: colors[r.config] || "var(--blue)" }}>
              {r.accuracy_pct}% ({r.correct}/{r.total})
            </div>
          </div>
          <div className="muted" style={{ width: 70 }}>{r.steps} steps</div>
        </div>
      ))}
      <p className="muted" style={{ marginTop: 14 }}>
        Reading: single agent matches the full system (94%) at 1/7 the cost; specialists carry the most value
        (removing them drops to 72%), memory helps modestly, the verifier adds none here.
      </p>
    </div>
  );
}

function Audit() {
  const [entries, setEntries] = useState([]);
  const [err, setErr] = useState(null);
  const load = () => getAudit().then((d) => setEntries(d.entries || [])).catch((e) => setErr(e.message));
  useEffect(() => { load(); }, []);
  if (err) return <div className="panel"><div className="result-err">API not reachable: {err}</div></div>;
  return (
    <div className="panel">
      <h2>Audit log <span className="pill">{entries.length} entries</span>
        <button className="btn-blue" style={{ float: "right", padding: "5px 12px" }} onClick={load}>Refresh</button></h2>
      <table>
        <thead><tr><th>Time (UTC)</th><th>Run</th><th>Actor</th><th>Action</th><th>Detail</th></tr></thead>
        <tbody>
          {entries.slice().reverse().map((e, i) => (
            <tr key={i}>
              <td className="muted">{(e.ts || "").slice(11, 19)}</td>
              <td>{e.run_id}</td><td>{e.actor}</td><td>{e.action}</td>
              <td className="muted">{(e.detail || "").slice(0, 60)}</td>
            </tr>
          ))}
          {entries.length === 0 && <tr><td colSpan="5" className="muted">No entries yet — run an incident in the Console.</td></tr>}
        </tbody>
      </table>
    </div>
  );
}

export default function App() {
  const [tab, setTab] = useState("console");
  return (
    <div className="app">
      <div className="header">
        <span className="dot" style={{ background: "var(--blue)" }} />
        <h1>AgentOS — Incident Response</h1>
      </div>
      <p className="sub">Multi-agent triage across Slack · logs · deploys · Jira, with human-approved actions.</p>
      <div className="tabs">
        {[["console", "Approval Console"], ["dashboard", "Ablation Dashboard"], ["audit", "Audit Log"]].map(([k, label]) => (
          <div key={k} className={`tab ${tab === k ? "active" : ""}`} onClick={() => setTab(k)}>{label}</div>
        ))}
      </div>
      {tab === "console" && <Console />}
      {tab === "dashboard" && <Dashboard />}
      {tab === "audit" && <Audit />}
    </div>
  );
}
