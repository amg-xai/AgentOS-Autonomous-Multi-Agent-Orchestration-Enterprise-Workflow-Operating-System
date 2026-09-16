"""LLM client (Gemini) with retries + on-disk response cache."""
import os, time, json, hashlib
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import warnings
warnings.filterwarnings("ignore")

load_dotenv()
_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
_llm = ChatGoogleGenerativeAI(model=_MODEL, temperature=0,
                              google_api_key=os.getenv("GOOGLE_API_KEY"))

_CACHE_DIR = ".llm_cache"
os.makedirs(_CACHE_DIR, exist_ok=True)

def _key(system, user):
    h = hashlib.sha256(f"{_MODEL}\x00{system}\x00{user}".encode()).hexdigest()
    return os.path.join(_CACHE_DIR, h + ".json")

def _extract_text(content) -> str:
    # Gemini returns a list of dicts like [{'type':'text','text':'...'}]; others return a plain string.
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict):
                parts.append(c.get("text", ""))
            else:
                parts.append(str(c))
        return "".join(parts)
    return str(content)

def call_llm(system: str, user: str, retries: int = 6) -> str:
    path = _key(system, user)
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))["response"]
    for attempt in range(retries):
        try:
            resp = _llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
            out = _extract_text(resp.content)          # <-- fixed extraction
            json.dump({"response": out}, open(path, "w", encoding="utf-8"))
            return out
        except Exception as e:
            if any(x in str(e) for x in ("429", "503", "rate", "UNAVAILABLE", "quota")):
                time.sleep(8 * (attempt + 1)); continue
            raise
        