# planner.py
# 将自然语言任务拆成有序的工具调用步骤（JSON array）
# 使用本地 Ollama (http://localhost:11434) 作为 LLM 后端

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3")  # 与你 ollama pull 的模型名一致

SYSTEM_PROMPT = """
You are a task planner. Given the user's goal, OUTPUT EXACTLY ONE JSON ARRAY (no extra text).
Each element in the array must be an object with these fields:
  - tool: one of ["lookup_word", "solve_math", "save_note", "ask"]
  - args: an object of named arguments for that tool (e.g. {"word":"agent"} or {"expr":"2+3"})
  - desc: short human-readable description of the step

If the user goal is ambiguous or missing parameters, return a single-element array:
  [{"tool":"ask", "args":{"question":"<what you need to ask user>"}, "desc":"ask for missing info"}]

Allowed tool names: lookup_word, solve_math, save_note, ask
"""

def call_local_ollama(messages, timeout=30):
    """
    Robust handler for Ollama HTTP chat responses that may be returned as NDJSON
    (multiple JSON lines, each containing a 'message' fragment). This function
    will:
      - try resp.json() (non-stream case)
      - otherwise iterate each non-empty line, parse JSON, extract message.content
      - concatenate all message.content fragments (in order) into one string
      - if nothing parsed, fall back to best-effort extraction or raw text

    Returns: assistant text (string) when possible, otherwise raw response text.
    """
    url = OLLAMA_URL.rstrip("/") + "/api/chat"
    payload = {"model": OLLAMA_MODEL, "messages": messages}
    resp = requests.post(url, json=payload, timeout=timeout)
    resp.raise_for_status()

    text = resp.text

    # 1) Fast path: try as single JSON document
    try:
        j = resp.json()
    except Exception:
        j = None

    # Helper to extract assistant text from a parsed JSON object if possible
    def extract_from_obj(obj):
        # common Ollama shape: {"choices":[{"message":{"role":"assistant","content":"..."}}]}
        if isinstance(obj, dict):
            if "choices" in obj and isinstance(obj["choices"], list) and len(obj["choices"])>0:
                msg = obj["choices"][0].get("message", {})
                if isinstance(msg, dict) and "content" in msg:
                    return msg.get("content")
            # older/other shape: {"message":{"role":"assistant","content":"..."}}
            if "message" in obj and isinstance(obj["message"], dict):
                c = obj["message"].get("content")
                if isinstance(c, str):
                    return c
            # other heuristic fields
            for k in ("text","generated_text","output"):
                if k in obj and isinstance(obj[k], str):
                    return obj[k]
        return None

    # 2) If single JSON parsed, try to extract assistant content
    if j is not None:
        content = extract_from_obj(j)
        if content is not None:
            return content
        # if parsed JSON but no direct assistant text, return pretty JSON
        try:
            return json.dumps(j, ensure_ascii=False)
        except Exception:
            return str(j)

    # 3) Handle NDJSON / streaming: parse line by line, collect fragments in order
    fragments = []
    for line in text.splitlines():
        ln = line.strip()
        if not ln:
            continue
        try:
            obj = json.loads(ln)
        except Exception:
            # skip unparsable lines
            continue
        # Extract message fragment
        frag = extract_from_obj(obj)
        if frag:
            fragments.append(frag)
            continue
        # fallback: sometimes assistant content nested deeper or under 'message'->'content'
        if isinstance(obj, dict) and "message" in obj and isinstance(obj["message"], dict):
            c = obj["message"].get("content")
            if isinstance(c, str):
                fragments.append(c)
                continue
    if fragments:
        # join fragments into single assistant string (preserve order)
        return "".join(fragments)

    # 4) as last resort, try to salvage a JSON block from full text
    try:
        first = text.index('{')
        last = text.rindex('}') + 1
        candidate = text[first:last]
        maybe = json.loads(candidate)
        content = extract_from_obj(maybe)
        if content:
            return content
        return json.dumps(maybe, ensure_ascii=False)
    except Exception:
        # give back raw text so we can debug in logs/screenshots
        return text

def plan(user_goal, chat_history=None):
    """
    Return dict: {"ok":True, "steps":[...], "raw": raw_text} or {"ok":False, "error":..., "raw": raw_text}
    chat_history: optional list of prior messages (same format as messages for LLM)
    """
    messages = [{"role":"system", "content": SYSTEM_PROMPT}]
    if chat_history:
        # chat_history expected as list of {"role":"user"/"assistant"/"system", "content":...}
        messages.extend(chat_history)
    messages.append({"role":"user", "content": f"Goal: {user_goal}\nReturn JSON steps as described."})

    try:
        raw = call_local_ollama(messages)
    except Exception as e:
        return {"ok": False, "error": f"LLM call failed: {e}", "raw": str(e)}

    # Try parse JSON out of raw - handle cases where LLM adds backticks or text
    text = raw.strip()
    # remove surrounding code fences if any
    if text.startswith("```") and text.endswith("```"):
        # naive strip of triple backticks
        text = "\n".join(text.splitlines()[1:-1])
    # find first '[' and last ']'
    try:
        first = text.index('[')
        last = text.rindex(']') + 1
        candidate = text[first:last]
        steps = json.loads(candidate)
        if not isinstance(steps, list):
            raise ValueError("planner output is not a JSON array")
        return {"ok": True, "steps": steps, "raw": raw}
    except Exception as e:
        # parsing failed: return raw for debugging
        return {"ok": False, "error": f"Planner parse failed: {e}", "raw": raw}