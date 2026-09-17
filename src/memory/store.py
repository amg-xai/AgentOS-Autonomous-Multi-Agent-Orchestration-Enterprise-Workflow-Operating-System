"""Persistent vector-store memory of past incidents (the team's incident history).
Vector store: Chroma. Embeddings: Gemini (reuses GOOGLE_API_KEY), cached on disk."""
import os, json, hashlib
import chromadb
from dotenv import load_dotenv
load_dotenv()

HISTORY = [
  {"id":"H01","owner":"payments-team","severity":"SEV-2","text":"Checkout returned 500s (NullPointerException) shortly after a payment-service deployment. Owner: payments-team. Severity: SEV-2. Resolved by rolling back."},
  {"id":"H02","owner":"platform-team","severity":"SEV-1","text":"A database host/config change made the primary DB unreachable, causing a full outage. Owner: platform-team. Severity: SEV-1. Resolved by reverting config."},
  {"id":"H03","owner":"frontend-team","severity":"SEV-3","text":"An oversized JavaScript bundle from a frontend deploy caused slow page loads. Owner: frontend-team. Severity: SEV-3. Fixed by lazy-loading."},
  {"id":"H04","owner":"payments-team","severity":"SEV-2","text":"Payment failures spiked after the gateway timeout was lowered too aggressively. Owner: payments-team. Severity: SEV-2. Fixed by restoring the timeout."},
  {"id":"H05","owner":"platform-team","severity":"SEV-2","text":"A cache TTL misconfiguration caused a cache stampede that overloaded the database CPU; the DB was a victim, not the cause. Caching is owned by platform-team. Severity: SEV-2."},
  {"id":"H06","owner":"platform-team","severity":"SEV-1","text":"A JWT signing-key rotation missed a service, causing mass 401 unauthorized errors. Auth is owned by platform-team. Severity: SEV-1."},
  {"id":"H07","owner":"payments-team","severity":"SEV-3","text":"Checkout errors traced to an external third-party payment provider outage; internal code unchanged. Integration owned by payments-team. Severity: SEV-3."},
  {"id":"H08","owner":"platform-team","severity":"SEV-2","text":"A service repeatedly OOM-killed and restarted due to an unbounded in-memory cache. Service owned by platform-team. Severity: SEV-2."},
  {"id":"H09","owner":"platform-team","severity":"SEV-3","text":"A CRITICAL alert was a false alarm from a broken synthetic monitor in one region; real users unaffected. Monitoring owned by platform-team. Severity: SEV-3."},
  {"id":"H10","owner":"platform-team","severity":"SEV-1","text":"Cascading failures across services traced to one slow upstream that added a synchronous write. Upstream owned by platform-team. Severity: SEV-1."},
  {"id":"H11","owner":"frontend-team","severity":"SEV-3","text":"Search silently returned empty results (HTTP 200, no errors) due to a wrong index name in config. Search owned by frontend-team. Severity: SEV-3."},
  {"id":"H12","owner":"platform-team","severity":"SEV-3","text":"An admin-tools refund dashboard returned 500s after a refactor, affecting only internal admins. Admin-tools owned by platform-team. Severity: SEV-3 (low impact)."},
  {"id":"H13","owner":"frontend-team","severity":"SEV-2","text":"Checkout broke when a frontend payload change dropped a required field. Owner: frontend-team. Severity: SEV-2."},
  {"id":"H14","owner":"payments-team","severity":"SEV-2","text":"Intermittent connection resets traced to an undersized DB connection pool after a config change. Owner: payments-team. Severity: SEV-2."},
]

_EMB_CACHE=".emb_cache"; os.makedirs(_EMB_CACHE, exist_ok=True)
_MODEL="gemini-embedding-001"

def _embed(text):
    p=os.path.join(_EMB_CACHE, hashlib.sha256((_MODEL+text).encode()).hexdigest()+".json")
    if os.path.exists(p): return json.load(open(p))
    from google import genai
    client=genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    r=client.models.embed_content(model=_MODEL, contents=text)
    vec=list(r.embeddings[0].values)
    json.dump(vec, open(p,"w")); return vec

_client=chromadb.PersistentClient(path=".chroma")

def _collection():
    col=_client.get_or_create_collection("incident_history")
    if col.count()==0:
        col.add(ids=[h["id"] for h in HISTORY],
                documents=[h["text"] for h in HISTORY],
                embeddings=[_embed(h["text"]) for h in HISTORY],
                metadatas=[{"owner":h["owner"],"severity":h["severity"]} for h in HISTORY])
    return col

def retrieve(query, k=3):
    col=_collection()
    res=col.query(query_embeddings=[_embed(query)], n_results=k)
    docs=res.get("documents",[[]])[0]
    return "\n".join(f"- {d}" for d in docs) if docs else "(no similar past incidents found)"
