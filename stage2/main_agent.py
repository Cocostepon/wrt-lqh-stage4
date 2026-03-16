# -*- coding: utf-8 -*-
# stage2/main_agent.py

from zhipuai import ZhipuAI
from tools import lookup_word, solve_math, save_note

client = ZhipuAI(api_key="406c7df7e3f942d7aa89981f4857a9a7.HZJLcNaOQHaATq2W")

# 1. 初始化对话记忆 [cite: 33]
# 存储格式为 [{"role": "user/assistant", "content": "..."}]
chat_history = [
    {"role": "system", "content": """你是一个学习助手。
    能力列表：
    1. 查单词：回复格式 TOOL:LOOKUP|ARG:单词
    2. 算数学题：回复格式 TOOL:MATH|ARG:算式
    3. 记笔记：回复格式 TOOL:NOTE|ARG:内容

    规则：
    - 如果用户指令模糊或缺少必要参数（如想记笔记但没给内容），请直接以自然语言追问用户，不要返回 TOOL 格式 [cite: 40, 41]。
    - 如果用户参考了之前的对话（如“那这个词呢？”），请结合历史记录判断意图 。
    """}
]


def run_agent(user_input):
    # 将用户输入加入记忆
    chat_history.append({"role": "user", "content": user_input})

    try:
        # 2. 调用 LLM，传入完整的 chat_history [cite: 33]
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=chat_history
        )
        res = response.choices[0].message.content

        # 3. 错误处理：LLM 输出解析 [cite: 36, 37]
        if "TOOL:" in res:
            # 执行工具逻辑
            if "TOOL:LOOKUP" in res:
                arg = res.split("|ARG:")[1] if "|ARG:" in res else ""
                result = lookup_word(arg)
            elif "TOOL:MATH" in res:
                arg = res.split("|ARG:")[1] if "|ARG:" in res else ""
                result = solve_math(arg)
            elif "TOOL:NOTE" in res:
                arg = res.split("|ARG:")[1] if "|ARG:" in res else ""
                result = save_note(arg)

            # 将工具执行结果也加入记忆，并反馈给用户
            chat_history.append({"role": "assistant", "content": result})
            return result
        else:
            # 如果是 LLM 的主动追问或普通对话
            chat_history.append({"role": "assistant", "content": res})
            return res

    except Exception as e:
        return f"【系统错误】连接大脑失败：{e}"


# 4. 多轮交互测试 [cite: 34, 45]
if __name__ == "__main__":
    print("--- 学习助手（第二阶段）已启动 ---")
    while True:
        u_input = input("用户: ")
        if u_input.lower() in ["exit", "quit"]: break
        print(f"Agent: {run_agent(u_input)}")