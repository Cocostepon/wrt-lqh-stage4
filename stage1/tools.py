# -*- coding: utf-8 -*-
"""
项目方向：学习助手 [cite: 98]
核心任务：封装3个核心工具函数 [cite: 13]
验收要求：明确的输入参数、输出格式、功能描述，且可独立调用 [cite: 14, 15]
"""


def lookup_word(word: str):
    """
    功能描述：查询英文单词的中文含义 。
    输入参数：word (str) - 目标英文单词。
    输出格式：返回包含单词释义的字符串。
    """
    # 模拟简单的词典数据库
    dictionary = {
        "agent": "n. 代理人；智能体 (在人工智能领域指能感知环境并采取行动的系统)。",
        "python": "n. 蟒蛇；一种高级编程语言。",
        "learning": "n. 学习；学问；知识。"
    }
    result = dictionary.get(word.lower(), "抱歉，暂未在词典中找到该单词。")
    return f"【查词助手】{word}: {result}"


def solve_math(expression: str):
    """
    功能描述：计算基础数学表达式的结果 。
    输入参数：expression (str) - 数学算式，如 '125 * 8'。
    输出格式：返回计算结果字符串。
    """
    try:
        # eval 可以将字符串作为数学表达式计算 [cite: 15]
        result = eval(expression)
        return f"【算题助手】计算结果为：{result}"
    except Exception as e:
        return f"【算题助手】计算出错：请确保输入的是正确的数学表达式。错误信息：{e}"


def save_note(content: str):
    """
    功能描述：将学习心得或重要信息保存到本地笔记文件 。
    输入参数：content (str) - 笔记内容。
    输出格式：返回保存成功的状态提示。
    """
    try:
        # 将内容追加到本地 notes.txt 文件中
        with open("notes.txt", "a", encoding="utf-8") as f:
            f.write(content + "\n---\n")
        return "【笔记助手】记录成功！内容已保存在本地 notes.txt 文件中。"
    except Exception as e:
        return f"【笔记助手】保存失败：{e}"


# --- 以下代码用于验证工具是否可独立调用 [cite: 15, 22] ---
if __name__ == "__main__":
    print("--- 正在进行工具独立运行验证 ---")

    # 测试查词
    print(lookup_word("agent"))

    # 测试算题
    print(solve_math("1024 / 8"))

    # 测试记笔记
    print(save_note("今天完成了 AI Agent 阶段 1 的环境配置和工具开发。"))

    print("\n验证完成！你可以截取上面的运行结果作为阶段 1 的验收截图。")