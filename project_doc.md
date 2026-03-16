## 项目文档：自定义 AI Agent（学习助手）

## 项目简介

本项目实现了一个基于大语言模型（LLM）的“学习助手”类 AI Agent。  
Agent 可以通过自然语言与用户交互，根据用户需求调用不同工具完成任务，例如：

- 查单词
- 计算数学表达式
- 记录学习笔记
- 生成学习周报

系统支持多轮对话，并能够在复杂任务下自动规划步骤，调用多个工具完成任务。

最终实现了一个 **可在命令行运行的智能 Agent**，并具备清晰的模块化结构，方便扩展更多工具与功能。

---

# 技术选型

## 大模型

本项目使用 **本地大模型 Ollama** 作为 LLM 推理服务，例如：

- `gemma3`
- `llama3`
- `qwen`

通过本地 HTTP API 调用：http://localhost:11434/api/generate

优点：

- 无需 API Key
- 运行稳定
- 数据完全本地化
- 成本为 0

---

## 编程语言

Python 3.8+

---

## 项目结构

项目采用模块化设计。

模块职责：

| 模块           | 功能            |
| ------------ | ------------- |
| main_agent   | CLI Agent 主程序 |
| planner      | 将复杂任务拆解为步骤    |
| orchestrator | 调用工具执行步骤      |
| tools        | 具体工具函数        |
| tests        | 自动化测试         |

---

# 核心功能

项目分为多个阶段实现：

---

## Stage1：基础 Agent

实现基础能力：

- 调用本地 LLM（Ollama）
- 解析用户意图
- 实现基础工具

工具包括：

1️⃣ 查单词

返回单词释义。

2️⃣ 数学计算

计算简单数学表达式。

3️⃣ 记录笔记

将内容写入 `notes.txt`。

---

## Stage2：多轮对话与记忆

在 Stage1 基础上增加：

### 多轮对话

Agent 维护 `chat_history`：

chat_history = []

### 参数缺失处理

当用户请求缺少必要信息时，Agent 会主动询问。

### Prompt 优化

通过 Prompt 指导 LLM：

- 当信息不足时询问

- 当可以调用工具时输出 JSON 指令

## Stage3：任务规划（Planner）

复杂任务需要多个步骤完成，例如：

生成本周学习周报

Agent 不直接回答，而是先进行 **任务规划**。

Planner 会生成步骤，例如：

[  
{"tool":"lookup_word","args":{"word":"agent"}},  
{"tool":"save_note","args":{"content":"..."}}  
]

## Stage3：工具调度（Orchestrator）

Orchestrator 负责：

1️⃣ 解析 Planner 输出  
2️⃣ 依次调用工具  
3️⃣ 收集结果  
4️⃣ 生成最终回答

执行流程：

用户请求
 ↓
Planner 生成计划
 ↓
Orchestrator 执行工具
 ↓
整合结果
 ↓
返回用户

# 运行方法

## 1 安装 Ollama

下载：

[https://ollama.com](https://ollama.com?utm_source=chatgpt.com)

安装后启动服务。

---

## 2 下载模型

例如：ollama pull gemma3

## 3 创建 Python 环境

python -m venv .venv

激活：

Windows

..venv\Scripts\activate

## 4 安装依赖

pip install pytest  
pip install python-dotenv  
pip install requests

## 5 启动 Agent

进入项目目录：

cd stage2

运行：

python main_agent.py

启动成功后：

--- 学习助手（本地 Ollama）已启动 ---  
输入 exit 或 quit 退出。

# 未来优化方向

### 1 引入 Agent 框架

例如：

- LangChain

- LlamaIndex

简化 Agent 架构。

---

### 2 扩展工具

新增工具：

- 天气查询

- 翻译

- 知识检索

- 文件总结

---

### 3 Web 前端

将 CLI Agent 扩展为：

- Web 页面

- 聊天界面

例如：

- Gradio

- Streamlit

- React

---

### 4 长期记忆

目前只保存短期对话。

未来可以加入：

- 向量数据库

- RAG 检索

- 长期记忆系统

# 总结

本项目实现了一个完整的 **AI Agent 系统原型**：

- 本地 LLM 推理（Ollama）

- 工具调用

- 多轮对话

- 任务规划

- 工具调度

- 自动化测试

系统结构清晰，可扩展性强，可作为 AI Agent 开发的基础框架。
