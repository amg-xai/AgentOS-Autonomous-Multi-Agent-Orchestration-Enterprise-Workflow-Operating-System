import os, time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()
_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
_llm = ChatGroq(model=_MODEL, temperature=0, api_key=os.getenv("GROQ_API_KEY"))

def call_llm(system: str, user: str, retries: int = 6) -> str:
    for attempt in range(retries):
        try:
            resp = _llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
            return resp.content if isinstance(resp.content, str) else str(resp.content)
        except Exception as e:
            if any(x in str(e) for x in ("429", "503", "rate", "UNAVAILABLE", "quota")):
                time.sleep(5 * (attempt + 1)); continue
            raise
    raise RuntimeError("LLM unavailable after retries — try again shortly.")