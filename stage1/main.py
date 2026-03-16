# stage1/main_agent.py
from zhipuai import ZhipuAI
from tools import lookup_word, solve_math, save_note

# 1. 初始化大脑 (填入你已经验证成功的 Key)
client = ZhipuAI(api_key="406c7df7e3f942d7aa89981f4857a9a7.HZJLcNaOQHaATq2W")


def run_agent(user_input):
    # 2. 告诉 LLM 如何选择工具
    prompt = f"""
    你是一个学习助手。请根据用户的输入，判断应该调用哪个工具：
    - 如果是查单词，回复格式为：TOOL:LOOKUP|ARG:单词
    - 如果是算数学题，回复格式为：TOOL:MATH|ARG:算式
    - 如果是记笔记，回复格式为：TOOL:NOTE|ARG:内容

    用户输入："{user_input}"
    """

    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}]
    )

    res = response.choices[0].message.content
    print(f"--- 大脑思考结果: {res} ---")

    # 3. 解析结果并自动执行工具
    if "TOOL:LOOKUP" in res:
        arg = res.split("|ARG:")[1]
        return lookup_word(arg)
    elif "TOOL:MATH" in res:
        arg = res.split("|ARG:")[1]
        return solve_math(arg)
    elif "TOOL:NOTE" in res:
        arg = res.split("|ARG:")[1]
        return save_note(arg)
    else:
        return "抱歉，我还没学会处理这个请求。"


# 4. 测试联动效果
if __name__ == "__main__":
    print(run_agent("帮我算一下 256 乘以 4"))
    print(run_agent("帮我查一下 agent 这个词"))