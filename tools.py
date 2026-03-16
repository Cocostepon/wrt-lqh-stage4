# -*- coding: utf-8 -*-
# stage2/tools.py

def lookup_word(word: str):
    """查询英文单词，增加参数为空的检查 """
    if not word or not word.strip():
        return "【错误】请输入要查询的单词，例如：'查单词 agent'。"

    dictionary = {
        "agent": "n. 代理人；智能体",
        "python": "n. 蟒蛇；一种编程语言。",
        "learning": "n. 学习；学问。"
    }
    result = dictionary.get(word.lower().strip(), "抱歉，暂未在词典中找到该单词。")
    return f"【查词助手】{word}: {result}"


def solve_math(expression: str):
    """计算数学题，增加异常捕获 [cite: 36, 37]"""
    if not expression or not expression.strip():
        return "【错误】请提供具体的数学算式，例如：'算一下 1+1'。"

    try:
        # 使用更安全的方式或捕获所有执行错误
        result = eval(expression, {"__builtins__": None}, {})
        return f"【算题助手】计算结果为：{result}"
    except Exception as e:
        return f"【错误】数学算式格式不正确（{e}）。请输入类似 '256 * 4' 的表达式。"


def save_note(content: str):
    """保存笔记，增加空内容检查 """
    if not content or not content.strip():
        return "【错误】笔记内容不能为空，请告诉我你想记录什么。"

    try:
        with open("notes.txt", "a", encoding="utf-8") as f:
            f.write(content.strip() + "\n---\n")
        return "【笔记助手】记录成功！"
    except Exception as e:
        return f"【错误】文件写入失败：{e}"