import json, sys
from dotenv import load_dotenv
load_dotenv()

# 导入 Stage2 和 Stage3 功能
from stage2.main_agent import run_agent as direct_run
from stage3.planner import plan
from stage3.orchestrator import execute_plan

def main():
    print("【Agent CLI】输入 'mode:planner' 或 'mode:direct' 切换模式，输入 exit 退出。")
    mode = "direct"
    while True:
        prompt = input("You: ").strip()
        if not prompt: continue
        if prompt.lower() in ("exit", "quit"): break
        if prompt.startswith("mode:"):
            mode = prompt.split(":",1)[1]
            print(f"已切换模式: {mode}")
            continue

        if mode == "direct":
            # 直接调用 Stage2 run_agent
            response = direct_run(prompt)
            print("Agent:", response)
        elif mode == "planner":
            # 通过 Planner 和 Orchestrator 执行
            p = plan(prompt)
            if not p["ok"]:
                print("【Planner 错误】", p.get("error"))
                print("原始输出:", p.get("raw", ""))
                continue
            steps = p["steps"]
            print("拆解步骤：", json.dumps(steps, ensure_ascii=False, indent=2))
            e = execute_plan(steps)
            if not e["ok"]:
                if e.get("ask"):
                    answer = input(e["ask"] + " ")
                    print("（请重新输入任务或实现更复杂的问答流）")
                else:
                    print("执行失败：", e.get("error"))
                continue
            print("执行完成，汇总结果：", e["summary"])
        else:
            print("无效模式，请输入 mode:planner 或 mode:direct。")

if __name__ == "__main__":
    main()
