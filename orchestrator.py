from tools import lookup_word, solve_math, save_note

def call_tool(step, context):
    tool = step.get("tool")
    args = step.get("args", {}) or {}

    # 处理占位符，例如 "$ctx.last_result"
    for k,v in list(args.items()):
        if isinstance(v, str) and v.startswith("$ctx."):
            key = v.split(".",1)[1]
            args[k] = context.get(key, "")

    if tool == "lookup_word":
        return {"ok": True, "result": lookup_word(args.get("word",""))}

    if tool == "solve_math":
        return {"ok": True, "result": solve_math(args.get("expr",""))}

    if tool == "save_note":
        content = args.get("content","")
        # 如果没有内容，尝试从上下文获取 last_result
        if not content:
            # 使用 last_result if exists
            fallback = context.get("last_result")
            if isinstance(fallback, dict):
                # if the last result is a dict with text, try common keys
                content = fallback.get("result") or fallback.get("entry") or str(fallback)
            elif fallback:
                content = str(fallback)

        # 仍无内容：调用 LLM 来生成总结文本（基于 context logs）
        if not content:
            # prepare prompt from context logs
            logs_excerpt = "\n".join(
                (str(v) if not isinstance(v, dict) else json.dumps(v, ensure_ascii=False))
                for v in context.get("log_texts", [])[-5:]
            )
            prompt = f"请根据以下信息生成一段简短的学习周报（2-5句）：\n{logs_excerpt}\n\n输出为自然语言文本。"
            try:
                generated = call_llm([{"role":"user","content":prompt}])
                # guard: if generated empty fallback to error
                if generated and isinstance(generated, str):
                    content = generated.strip()
            except Exception as e:
                # can't generate -> return ask to user
                return {"ok": False, "ask": "无法自动生成笔记内容，请手动输入你要保存的笔记内容。"}

        # 最终仍为空 -> ask
        if not content:
            return {"ok": False, "ask": "请提供要保存的笔记内容。"}

        # call save_note tool
        return {"ok": True, "result": save_note(content)}

    return {"ok": False, "error": f"unknown tool {tool}"}

def execute_plan(steps):
    """依次执行拆解步骤，并返回汇总结果或向用户提问。"""
    context = {}
    logs = []
    for i, step in enumerate(steps):
        res = call_tool(step, context)
        logs.append({"step": step, "result": res})
        if not res.get("ok"):
            return {"ok": False, "logs": logs, "ask": res.get("ask"), "error": res.get("error")}
        # 保存执行结果供后续使用
        context[f"step_{i}_out"] = res["result"]
        context["last_result"] = res["result"]
    # 简单整合所有输出为文本
    summary = "；".join(str(log["result"]) for log in logs)
    return {"ok": True, "logs": logs, "summary": summary, "context": context}
