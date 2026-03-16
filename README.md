# AI-Agent-Plus 学习助手项目
## 项目简介

本项目实现了一个基于 **AI Agent 架构** 的学习助手系统。
系统能够通过本地大语言模型（LLM）进行自然语言理解，并根据用户需求调用不同工具完成任务，例如：

* 查询单词含义
* 进行数学计算
* 记录学习笔记
* 生成学习周报并保存为文件

该项目主要用于学习 **AI Agent 架构设计、工具调用机制以及本地大模型集成**。

## 项目功能

### 1. 查单词助手

用户可以输入单词，Agent 会返回单词的含义。
示例：
```
用户: 查单词 agent
Agent: 【查词助手】agent：代理人；智能体
```

### 2. 数学计算助手

支持简单数学表达式计算。
示例：
```
用户: 算 12*34
Agent: 【算题助手】计算结果为：408
```

### 3. 笔记记录功能

用户可以通过自然语言记录学习笔记，系统会保存到 `notes.txt`。
示例：
```
用户: 保存笔记: 今天学习了AI Agent架构
Agent: 【笔记助手】记录成功！
```

### 4. 多轮对话记忆

Agent 可以记住上下文信息，并在后续对话中使用。

示例：

```
用户: 查 agent
用户: 那它的复数形式呢？
Agent: agents 的含义为……
```

### 5. 周报生成

系统可以根据学习记录生成本周学习周报，并保存为文件。

示例：

```
用户: 生成周报并保存为 myreport.txt
Agent: 已生成周报并保存。
```

---

## 项目结构

```
AI-Agent-Plus
│
├─ stage2
│   ├─ main_agent.py        # Agent 主程序
│   ├─ tools.py             # 工具函数（查词、计算、笔记等）
│   ├─ planner.py           # 任务规划模块
│   ├─ orchestrator.py      # 工具调度模块
│   ├─ notes.txt            # 笔记存储文件
│   ├─ tests                # 测试用例
│   └─ test_cases.md        # 测试案例说明
│
└─ README.md
```

---

## 技术架构

本项目参考 **AI Agent 常见架构设计**：

```
用户输入
   ↓
Orchestrator（任务调度）
   ↓
Planner（任务规划）
   ↓
Tools（工具执行）
   ↓
LLM（本地 Ollama 模型）
```

主要技术：

* Python
* 本地 LLM（Ollama）
* Tool Calling 机制
* 多轮对话上下文管理

---

## 环境配置

### 1. 克隆仓库

```
git clone https://github.com/xxx/AI-Agent-Plus.git
```

进入项目目录：

```
cd AI-Agent-Plus
```

---

### 2. 创建虚拟环境

```
python -m venv .venv
```

激活环境：

Windows：

```
.venv\Scripts\activate
```

---

### 3. 安装依赖

```
pip install requests python-dotenv
```

---

### 4. 启动本地 LLM（Ollama）

安装 Ollama 并下载模型：

```
ollama pull gemma3
```

启动 Ollama：

```
ollama serve
```

---

### 5. 运行 Agent

```
python stage2/main_agent.py
```

---


## 项目贡献

本项目由以下成员共同完成：

**王若亭**
**李钦航**

---

## 项目说明

本项目主要用于：

* 学习 AI Agent 系统设计
* 探索大模型与工具结合的应用
* 实践多轮对话与任务规划机制

仅用于学习和研究用途。
