# main_agent.py (智能版)
# Learning Assistant — local Ollama backend, tools-based agent, auto planner for reports.
# Drop-in replacement for previous main_agent.py

import os
import json
import re
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3")

# Import your tools (assumed to exist)
from tools import lookup_word, solve_math, save_note

# --- System prompt: guide the model to use TOOL:... when appropriate ---
SYSTEM_PROMPT = """你是一个学习助手。
当用户要求执行工具（查单词/算题/保存笔记/保存文件/生成报告）时，请严格使用工具调用格式，不要仅用自然语言说明。
工具调用格式示例：
- 查单词: TOOL:LOOKUP|ARG:agent
- 算题: TOOL:MATH|ARG:12*34
- 保存笔记: TOOL:NOTE|ARG:这里是笔记内容
- 保存文件: TOOL:FILE|ARG:filename.txt::文件内容
- 生成报告（当需要自动生成并保存周报时，也可以返回 TOOL:GENERATE|ARG:简短指令）

如果信息不足（比如用户说“记笔记”但没给内容），请用自然语言主动提问，等待用户补充（不要返回 TOOL 指令）。
"""

# chat_history stores dicts of {"role":..., "content":...}
chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]

# --- Robust Ollama caller (accepts messages list or a single prompt string) ---
def call_local_ollama(messages, timeout=30):
    """
    messages: either a list of {"role","content"} or a plain string prompt.
    Returns assistant text (string). Robust to NDJSON / stream-like responses.
    """
    if isinstance(messages, str):
        payload_messages = [{"role": "user", "content": messages}]
    else:
        payload_messages = messages

    url = OLLAMA_URL.rstrip("/") + "/api/chat"
    payload = {"model": OLLAMA_MODEL, "messages": payload_messages}
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        raise requests.exceptions.RequestException(f"call_local_ollama request failed: {e}")

    text = resp.text

    # Try fast json parse
    try:
        j = resp.json()
    except Exception:
        j = None

    def extract_from_obj(obj):
        if isinstance(obj, dict):
            # Ollama often returns choices -> message -> content
            if "choices" in obj and isinstance(obj["choices"], list) and len(obj["choices"])>0:
                msg = obj["choices"][0].get("message", {})
                if isinstance(msg, dict) and "content" in msg:
                    return msg.get("content")
            if "message" in obj and isinstance(obj["message"], dict):
                c = obj["message"].get("content")
                if isinstance(c, str):
                    return c
            for k in ("text", "generated_text", "output"):
                if k in obj and isinstance(obj[k], str):
                    return obj[k]
        return None

    # 1) If parsed JSON, try extract
    if j is not None:
        content = extract_from_obj(j)
        if content is not None:
            return content
        try:
            return json.dumps(j, ensure_ascii=False)
        except Exception:
            return str(j)

    # 2) NDJSON / streaming: parse line by line and collect fragments
    fragments = []
    for line in text.splitlines():
        ln = line.strip()
        if not ln:
            continue
        try:
            obj = json.loads(ln)
        except Exception:
            # skip unparsable line
            continue
        frag = extract_from_obj(obj)
        if frag is not None:
            fragments.append(frag)
            continue
        # fallback: nested message.content
        if isinstance(obj, dict) and "message" in obj and isinstance(obj["message"], dict):
            c = obj["message"].get("content")
            if isinstance(c, str):
                fragments.append(c)
                continue

    if fragments:
        # join and normalize whitespace (model may stream tokens)
        return "".join(fragments).replace("\n\n\n", "\n\n")

    # 3) Last resort: try to extract first JSON block
    try:
        first = text.index("{")
        last = text.rindex("}") + 1
        candidate = text[first:last]
        maybe = json.loads(candidate)
        c = extract_from_obj(maybe)
        if c:
            return c
        return json.dumps(maybe, ensure_ascii=False)
    except Exception:
        # return raw text for debugging
        return text

# --- Helper: save arbitrary file ---
def save_file(filename: str, content: str):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return True, f"文件已保存：{filename}"
    except Exception as e:
        return False, f"文件保存失败：{e}"

# --- Helper: generate report (try use notes.txt if present) ---
def generate_report(use_notes=True, user_hint=None):
    """
    Generate a short weekly learning report.
    If use_notes and notes.txt exists, feed recent notes to LLM for summary.
    user_hint: optional string from user describing what they want.
    """
    notes_text = ""
    notes_path = "notes.txt"
    if use_notes and os.path.exists(notes_path):
        try:
            with open(notes_path, "r", encoding="utf-8") as f:
                notes_text = f.read().strip()
        except Exception:
            notes_text = ""

    prompt_parts = []
    if user_hint:
        prompt_parts.append(f"用户说明：{user_hint}\n")
    if notes_text:
        # Use last ~2000 chars of notes to avoid too long prompts
        prompt_parts.append("参考笔记（用于生成摘要）：\n" + notes_text[-2000:])
    prompt_parts.append(
        "请基于以上信息生成一份简短的本周学习周报，结构：一、本周完成（每项1-2句）；二、遇到的问题；三、下周计划（1-3条）。输出纯文本。"
    )
    prompt = "\n\n".join(prompt_parts)
    try:
        out = call_local_ollama(prompt)
        return out.strip()
    except Exception as e:
        return f"【错误】生成周报失败：{e}"

# --- Tool dispatcher (parses TOOL:... outputs) ---
def handle_tool_command(res_text: str):
    """
    Parse strings like:
      TOOL:LOOKUP|ARG:word
      TOOL:MATH|ARG:1+1
      TOOL:NOTE|ARG:content
      TOOL:FILE|ARG:filename.txt::content
      TOOL:GENERATE|ARG:hint
    Return (ok, result_text)
    """
    try:
        if "TOOL:" not in res_text:
            return False, None
        t_index = res_text.index("TOOL:")
        tail = res_text[t_index:]
        # find tool name
        tool = None
        arg = ""
        if "|ARG:" in tail:
            tool_part, arg = tail.split("|ARG:", 1)
            tool = tool_part.replace("TOOL:", "").strip()
            arg = arg.strip()
        else:
            # fallback: split by whitespace
            parts = tail.split()
            tool = parts[0].replace("TOOL:", "").strip() if parts else None
            if "ARG:" in tail:
                arg = tail.split("ARG:", 1)[1].strip()
        if not tool:
            return False, "【错误】解析工具失败"

        tool_upper = tool.upper()
        if tool_upper == "LOOKUP":
            return True, lookup_word(arg)
        if tool_upper == "MATH":
            return True, solve_math(arg)
        if tool_upper == "NOTE":
            # save_note returns a human-friendly string
            return True, save_note(arg)
        if tool_upper == "FILE":
            # expect filename::content
            if "::" in arg:
                filename, content = arg.split("::", 1)
                ok, msg = save_file(filename.strip(), content)
                return True, msg if ok else f"【错误】{msg}"
            else:
                return True, "【错误】FILE 格式错误，正确格式：filename::content"
        if tool_upper == "GENERATE":
            # treat arg as hint
            report = generate_report(use_notes=True, user_hint=arg)
            return True, report

        return False, "【错误】未知工具: " + tool
    except Exception as e:
        return False, f"【系统错误】工具执行异常：{e}"

# --- Main agent function ---
def run_agent(user_input: str):
    # append user message
    chat_history.append({"role": "user", "content": user_input})

    # quick local triggers (smart defaults)
    try:
        # If user explicitly asks to generate/save report, do an internal planner flow:
        # detect "周报" and keywords "保存" / "保存为 <filename>"
        lower = user_input.lower()
        if ("周报" in user_input) or ("生成周报" in lower):
            # if user supplied a filename via "保存为 X" or "保存 到 X"
            filename_match = re.search(r"保存为\s*([^\s，,]+)|保存到\s*([^\s，,]+)", user_input)
            filename = None
            if filename_match:
                filename = filename_match.group(1) or filename_match.group(2)
            # optional short hint: user may say "正式语气" etc.
            user_hint = None
            # generate report (prefer notes if present)
            report_text = generate_report(use_notes=True, user_hint=user_hint)
            # always save to notes.txt via save_note (keeps history)
            save_note(report_text)
            # if filename specified, also save to that file
            if filename:
                ok, msg = save_file(filename, report_text)
                if ok:
                    chat_history.append({"role": "assistant", "content": f"已生成周报并保存到 {filename}。"})
                    return f"已生成周报并保存到 {filename}。\n\n{report_text}"
                else:
                    chat_history.append({"role": "assistant", "content": f"周报生成，但保存到 {filename} 失败：{msg}"})
                    return f"周报已生成，但保存到 {filename} 失败：{msg}\n\n{report_text}"
            else:
                # saved into notes.txt by save_note
                chat_history.append({"role": "assistant", "content": "已生成周报并保存到 notes.txt。"})
                return f"已生成周报并保存到 notes.txt。\n\n{report_text}"

        # otherwise, call LLM to ask what to do / or to generate next
        raw = call_local_ollama(chat_history)
        res = raw if isinstance(raw, str) else str(raw)

        # If LLM returns TOOL:... pattern, handle it
        if "TOOL:" in res:
            ok, result = handle_tool_command(res)
            if ok:
                # push assistant tool result into history
                chat_history.append({"role": "assistant", "content": result})
                return result
            else:
                # tool parsing/execution error - return the message
                chat_history.append({"role": "assistant", "content": str(result)})
                return str(result)

        # Otherwise, normal assistant response (may be a follow-up question)
        chat_history.append({"role": "assistant", "content": res})
        return res

    except requests.exceptions.RequestException as e:
        return f"【系统错误】无法连接本地 LLM：{e}"
    except Exception as e:
        return f"【系统错误】运行时异常：{e}"

# --- CLI entrypoint ---
if __name__ == "__main__":
    print("--- 学习助手（智能版，本地 Ollama）已启动 ---")
    print("输入 exit 或 quit 退出。示例：'生成周报并保存为 myreport.txt'；'查单词 agent'；'算 12*34'；'记笔记 今天学了...'")
    while True:
        try:
            u_input = input("用户: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n退出。")
            break
        if not u_input:
            continue
        if u_input.lower() in ["exit", "quit"]:
            break
        out = run_agent(u_input)
        print(f"Agent: {out}")