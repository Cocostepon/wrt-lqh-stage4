# 阶段 1：LLM 调用与工具设计总结

### 1. 框架选择

- [cite_start]**编程语言**：Python 3.10.8 [cite: 10]
- [cite_start]**大模型 (LLM)**：智谱 AI - GLM-4-Flash [cite: 117]
- **设计思路**：本项目采用纯 Python 结合 ZhipuAI SDK 实现。通过编写系统 Prompt 约束模型输出固定格式的意图标识，利用逻辑判断触发对应的工具函数。

### [cite_start]2. 工具设计说明 [cite: 13, 14]

本项目封装了 3 个核心工具函数：

1. **`lookup_word(word)`**
   - **输入**：英文单词。
   - **输出**：对应的中文释义。
2. **`solve_math(expression)`**
   - **输入**：数学表达式（如 256 * 4）。
   - **输出**：计算后的数值结果。
3. **`save_note(content)`**
   - **输入**：需要记录的文本内容。
   - **输出**：本地文件 `notes.txt` 的保存状态。

### [cite_start]3. LLM 与工具联动逻辑 [cite: 17]

模型接收用户输入后，判断属于哪类任务并提取参数，按 `TOOL:工具名|ARG:参数` 格式返回。主程序解析该字符串后，自动调用 `tools.py` 中对应的函数。

### [cite_start]4. 遇到的问题及解决方法

- **问题 1：缺少 sniffio 依赖**
  - **现象**：报错 `ModuleNotFoundError: No module named 'sniffio'`。
  - **解决**：通过 `pip install sniffio` 手动安装缺失依赖。
- **问题 2：API Key 编码错误**
  - **现象**：报错 `UnicodeEncodeError: 'ascii' codec can't encode...`。
  - **解决**：发现是 API Key 配置中混入了非英文字符或中文引号，清理字符串并确保使用英文半角引号后恢复正常。
