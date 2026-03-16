import os, requests, json, traceback

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3")

def try_parse_json(text):
    # 尝试多种解析方式：整段 JSON、按行 NDJSON、首尾 {...} 块
    text = text.strip()
    # 1. 整体 json
    try:
        return json.loads(text), "whole"
    except Exception:
        pass
    # 2. 按行解析（NDJSON）
    lines = [ln for ln in text.splitlines() if ln.strip()]
    for ln in reversed(lines):
        try:
            return json.loads(ln), "line"
        except Exception:
            continue
    # 3. 找第一个 { ... } 块
    try:
        first = text.index('{')
        last = text.rindex('}') + 1
        cand = text[first:last]
        return json.loads(cand), "block"
    except Exception:
        pass
    return None, None

def main():
    url = OLLAMA_URL + "/api/chat"
    payload = {"model": OLLAMA_MODEL, "messages":[{"role":"user","content":"查单词 agent"}]}
    print("POST ->", url)
    try:
        r = requests.post(url, json=payload, timeout=30)
    except Exception as e:
        print("Request failed:", e)
        return
    print("HTTP STATUS:", r.status_code)
    text = r.text
    print("\n--- RAW RESPONSE (first 2000 chars) ---\n")
    print(text[:2000])
    print("\n--- END RAW ---\n")
    # 尝试解析
    j, how = try_parse_json(text)
    if j is None:
        print("Could not parse JSON from response.")
        return
    print("Parsed JSON (method={}): keys={}".format(how, list(j.keys()) if isinstance(j, dict) else type(j)))
    # If it's an Ollama-style 'choices' structure, print assistant preview
    try:
        if isinstance(j, dict) and "choices" in j and isinstance(j["choices"], list) and len(j["choices"])>0:
            msg = j["choices"][0].get("message", {})
            print("\nAssistant preview:\n", msg.get("content","(no content)"))
    except Exception:
        print("Error while showing assistant preview:\n", traceback.format_exc())

if __name__ == '__main__':
    main()
