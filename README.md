# ReAct Agent

> 🎯 **一个学习型 AI Agent 项目** — 从零手写，不依赖任何 Agent 框架，用于深入理解 Agent 的每一个齿轮如何咬合运转。

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 💡 关于这个项目

**作者**：笨笨 — 热爱编程与 AI 技术的探索者

**初心**：对大语言模型之上那片神奇地带——**Agentic AI** 尤为着迷。

从工具调用、记忆管理、多模型协作，到自主规划与推理……这些让 LLM 从"能说话"变成"能做事"的机制，正是这个项目想要亲手弄明白的东西。

**特点**：
- 🛠️ **从零手写**：不依赖 LangChain、AutoGPT 等框架，每一行代码都是亲手打造
- 📚 **边学边造**：在理解原理的过程中实践，在实践中深化理解
- 🔍 **深入本质**：不满足于"会用"，更想搞清楚"为什么是这样"
- 🎨 **简洁优雅**：用最少的代码实现最核心的功能，方便学习理解

**适合**：
- 想深入理解 Agent 原理的开发者
- 正在学习 LLM 应用的同学
- 对 AI Agent 内部机制好奇的探索者
- 需要轻量级 Agent 实现的项目

---

## ✨ 核心特性

- **🧠 智能推理**：ReAct 循环（思考 → 行动 → 观察 → 回答）
- **🔧 丰富工具**：22 个内置工具，覆盖文件、网络、系统、技能操作
- **📚 技能系统**：支持标准 Skills 格式，按需加载，可执行脚本
- **🛡️ 错误恢复**：自动重试机制，智能错误处理，永不异常退出
- **📦 模块架构**：清晰的职责分离，易于扩展和测试
- **🎯 精准提示**：优化的系统提示词 + 详细的工具文档
- **🎨 美化界面**：Rich 面板、代码高亮、Markdown 渲染
- **🌈 多主题**：6 种配色主题，支持动态切换
- **📊 会话导出**：Markdown/HTML 格式导出
- **⚡ 极速启动**：延迟加载优化，0.5 秒快速启动

---

## 🚀 快速开始

### 1. 安装

```bash
# 克隆项目
git clone <your-repo>
cd reason_act_agent

# 安装依赖
uv sync
```

### 2. 配置

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env，设置 API Key
# ONEAPI_API_KEY=your_key_here
```

### 3. 运行

```bash
# 交互式运行
uv run agent.py .

# 或指定项目目录
uv run agent.py /path/to/your/project
```

### 4. 体验

```
💬 请输入任务: 列出所有 Python 文件

💭 Thought: 需要列出目录中的 Python 文件
🔧 Action: list_dir(directory=".", include="*.py")

✅ Final Answer: 项目包含 5 个 Python 文件...
```

---

## 📖 使用示例

### 基础用法

```python
from reason_action_agent.agent import ReActAgent
from reason_action_agent.config import load_config

# 加载配置
config = load_config()
config.project_directory = "/path/to/project"

# 创建 Agent
agent = ReActAgent(config=config)

# 执行任务
result = agent.run("读取 README.md 的前 20 行并总结")
print(result)
```

### 自定义工具

```python
from reason_action_agent.tools import tool

@tool
def my_custom_tool(query: str) -> str:
    """
    自定义工具示例
    
    使用场景：
    - 查询数据库：my_custom_tool("SELECT * FROM users")
    - 调用 API：my_custom_tool("api_endpoint")
    
    参数说明：
    - query: 查询语句或参数
    
    示例：
    - my_custom_tool("test query")
    """
    # 实现你的逻辑
    return "结果..."

# Agent 会自动发现并注册工具
agent = ReActAgent()
```

---

## 🏗️ 项目架构

```
reason_action_agent/
├── agent.py              # 核心推理循环 + 智能错误恢复
├── config.py             # 配置管理（dataclass + 环境变量）
├── exceptions.py         # 异常定义（含错误处理策略）
├── message_manager.py    # 消息列表管理（持久化历史）
├── tag_parser.py         # 标签解析器
├── model_clients.py      # 模型客户端（自动重试 + 错误恢复）
├── prompts.py            # 系统提示模板
├── cli.py                # CLI 入口（斜杠命令 + Tab 补全）
├── session_logger.py     # 日志记录
├── session_exporter.py   # 会话导出（Markdown/HTML）
├── skill_manager.py      # 技能管理（标准 Skills）
├── rich_display.py       # Rich 美化显示
├── themes.py             # 主题配置（6 种主题）
├── input_manager.py      # 输入管理（自动补全）
└── tools/                # 工具模块
    ├── __init__.py
    ├── registry.py       # 工具注册器
    ├── file_tools.py     # 文件操作（9 个工具）
    ├── web_tools.py      # 网络工具（3 个工具）
    ├── system_tools.py   # 系统工具（5 个工具）
    └── skill_tools.py    # 技能工具（5 个工具）
```

---

## 🔧 内置工具（22 个）

### 📁 文件操作（9 个）

| 工具 | 功能 | 亮点 |
|------|------|------|
| `read_file` | 读取文件内容 | 支持行号范围、编码检测 |
| `write_to_file` | 写入文件 | 支持追加模式、自动创建目录 |
| `edit_file` | 编辑文件 | 查找替换，精确修改 |
| `list_dir` | 列出目录 | 树形结构、递归、过滤 |
| `search_files` | 搜索内容 | 支持正则、文件过滤 |
| `delete_file` | 删除文件/目录 | 支持递归删除 |
| `rename_file` | 重命名/移动 | 支持覆盖 |
| `copy_file` | 复制文件/目录 | 支持覆盖 |
| `run_terminal_command` | 执行命令 | 工作目录、超时控制 |

**示例**：
```python
# 分段读取大文件
read_file(file_path="/tmp/large.py", start_line=1, end_line=50)

# 精确修改配置
edit_file(file_path="/tmp/config.py", old_string="DEBUG=False", new_string="DEBUG=True")

# 搜索代码中的 TODO
search_files(pattern="# TODO", include="*.py")
```

### 🌐 网络工具（3 个）

| 工具 | 功能 | 示例 |
|------|------|------|
| `get_weather` | 获取天气 | `get_weather("北京")` |
| `web_search` | 搜索网页 | `web_search("Python 教程")` |
| `fetch_url` | 抓取网页 | `fetch_url("https://...")` |

**示例**：
```python
# 查询实时天气
get_weather(city="北京")

# 搜索网络资源
web_search(query="Python 最佳实践", max_results=5)
```

### ⚙️ 系统工具（5 个）

| 工具 | 功能 | 示例 |
|------|------|------|
| `current_time` | 获取当前时间 | `current_time("Asia/Shanghai")` |
| `get_env` | 获取环境变量 | `get_env("PATH")` |
| `set_env` | 设置环境变量 | `set_env("DEBUG", "1")` |
| `list_env` | 列出环境变量 | `list_env("PATH")` |
| `get_system_info` | 获取系统信息 | `get_system_info()` |

---

## 🛡️ 智能错误恢复

遇到模型输出格式异常时，自动尝试修复：

```python
# 问题：模型输出遗漏标签
"需要读取文件\nread_file('/tmp/test.txt')"

# 自动修复为：
"<thought>需要读取文件</thought>\n<action>read_file('/tmp/test.txt')</action>"
```

**三层防御**：
1. **格式检测**：识别缺失的标签
2. **智能修复**：自动补全标签
3. **友好提示**：无法修复时引导模型重新输出

---

## 📊 对比总结

| 维度 | 优化前 | 优化后 |
|------|--------|--------|
| **工具数量** | 6 个 | **17 个** |
| **配置管理** | 散落各处 | `config.py` 统一管理 |
| **工具扩展** | 修改源码 | `@tool` 装饰器注册 |
| **错误处理** | 直接崩溃 | 智能修复 + 重试 |
| **文档质量** | 简单 Args | 使用场景 + 参数说明 + 示例 |
| **提示词** | 1,800 字符 | 7,000 字符（优化结构） |
| **代码质量** | 单体架构 | 模块化、可测试 |

---

## 🎯 核心改进

### 1. 配置管理

```python
from reason_action_agent.config import load_config

config = load_config()  # 自动从 .env 加载
config.model.name = "gpt-4"
config.log.enabled = True
```

### 2. 工具注册

```python
from reason_action_agent.tools import tool

@tool
def my_tool(x: int) -> int:
    """工具说明"""
    return x * 2
```

### 3. 异常处理

```python
from reason_action_agent.exceptions import ModelOutputError

try:
    agent.run(task)
except ModelOutputError as e:
    print(f"错误: {e}")
    print(f"原始输出: {e.raw_output}")
```

### 4. CLI 增强

```bash
uv run agent.py . --model gpt-4 --protocol openai
uv run agent.py . --no-log
uv run agent.py . --log-dir ./logs
```

---

## 🔌 扩展建议

1. **添加工具**：在 `tools/` 目录创建新模块，使用 `@tool` 装饰器
2. **流式输出**：在 `model_clients.py` 添加流式调用支持
3. **记忆系统**：新增 `memory.py` 管理对话历史
4. **多 Agent 协作**：基于 `ToolRegistry` 扩展 Agent 间通信
5. **工具验证**：添加参数校验和类型检查

---

## 📝 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MODEL_PROTOCOL` | 模型协议（openai/anthropic） | `openai` |
| `ONEAPI_API_KEY` | API Key | - |
| `ONEAPI_BASE_URL` | API Base URL | `https://oneapi-comate.baidu-int.com/v1` |
| `ONEAPI_MODEL` | 模型名称 | `deepseek-v4-flash` |
| `AGENT_LOG_DIR` | 日志目录 | `logs` |
| `AGENT_LOG_ENABLED` | 是否启用日志 | `true` |

---

## 🧪 测试

```bash
# 运行所有测试
uv run python -c "from reason_action_agent.tools import get_default_tools; print(f'✓ {len(get_default_tools())} 个工具')"

# 测试工具
uv run python -c "from reason_action_agent.tools import list_dir; print(list_dir('.'))"
```

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- ReAct 论文：[ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- OpenAI & Anthropic：提供强大的模型 API
- uv：快速的 Python 包管理器

---

## 🤔 为什么从零手写？

在 LangChain、AutoGPT、AgentGPT 等优秀框架已经成熟的今天，为什么还要从零手写一个 Agent？

**因为理解原理比会用工具更重要**。

### 📚 学习的三个层次

1. **会用**：知道如何调用 API、使用框架解决问题
2. **理解**：明白工具背后的原理、设计权衡
3. **创造**：能根据需求设计自己的解决方案

这个项目正处于**第二层**——通过亲手实现，深入理解 Agent 的核心机制：

- ❓ **ReAct 循环**：为什么是 Thought → Action → Observation？怎么让模型遵循这个模式？
- ❓ **工具调用**：如何解析自然语言中的工具调用意图？参数如何提取和验证？
- ❓ **错误恢复**：模型输出不符合预期时，如何智能引导而不是直接失败？
- ❓ **上下文管理**：多轮对话中如何管理消息历史？什么时候该保留、什么时候该丢弃？
- ❓ **提示工程**：什么样的提示词能让模型更好地理解和执行？

### 🎯 这些问题，只有在亲手实现中才能真正理解

框架的抽象是好事，它让我们快速上手。但抽象也意味着**细节的隐藏**。

当你想知道：
- 为什么模型有时候"不听话"？
- 如何让 Agent 更稳定、更智能？
- 不同设计选择的 trade-off 是什么？

**只有自己造过轮子，才能真正理解轮子的精妙**。

### 💪 这个项目的价值

如果你：
- 🎓 正在学习 LLM 应用开发
- 🔬 想研究 Agent 的内部机制
- 🏗️ 需要定制自己的 Agent 实现
- 🤔 对现有框架感到困惑或不满足

那么这个项目适合你。

**代码不多（~1800 行），但该有的都有**：
- 清晰的模块划分
- 完整的错误处理
- 详细的中文注释
- 丰富的使用示例

**读一遍代码，胜过看十遍教程**。

---

## 📮 交流与反馈

如果你也在探索 Agentic AI，欢迎交流：

- 🐛 发现问题？提个 [Issue](../../issues)
- 💡 有想法？开个 [Discussion](../../discussions)
- 🔄 有改进？欢迎 [Pull Request](../../pulls)

**一起学习，一起进步** 🚀

---

## 📚 技能系统

### 技能格式（标准 YAML Frontmatter + Markdown）

```markdown
---
name: python-expert
description: Python 编程专家，精通最佳实践和设计模式
version: 1.0.0
author: your-name
tags:
  - python
  - coding
---

# Python 编程专家

技能内容...

## 核心能力
- 代码质量：遵循 PEP 8 规范
- 设计模式：熟练运用常见设计模式
```

### 技能目录结构

```
~/.agent/skills/           # 全局技能
├── python-expert/
│   ├── SKILL.md          # 技能主文件
│   ├── scripts/          # 可执行脚本
│   │   ├── analyze.py
│   │   └── optimize.py
│   └── references/       # 参考文档
│       └── best_practices.md
```

### 技能命令

```bash
# 列出技能
/skills

# 安装技能
/skill install https://.../skill.md
/skill install /path/to/skill-dir --project

# 查看技能详情
/skill info python-expert

# 加载技能
/skill load python-expert

# 执行技能脚本
/skill run python-expert analyze.py --args

# 读取参考文档
/skill read python-expert best_practices.md
```

---

## ⚠️ 安全说明

### 终端命令执行

**当前设置**：终端命令执行**无确认提示**，直接执行。

**原因**：
- 提升使用体验，减少中断
- Agent 已经过系统提示词约束
- 适用大多数开发场景

**后续完善方向**：
- 配置化：可设置是否需要确认
- 命令白名单：只对危险命令确认
- 智能判断：根据命令内容决定

**注意事项**：
- ⚠️ Agent 可以执行任意终端命令
- ⚠️ 请在受信任的环境中使用
- ⚠️ 敏感操作建议人工审核

---

## 🎓 学习价值

这个项目适合想深入理解 Agent 原理的开发者：

| 学习点 | 文件 | 核心代码 |
|--------|------|----------|
| ReAct 循环 | `agent.py` | `run()` 方法 |
| 工具注册 | `tools/registry.py` | `@tool` 装饰器 |
| 消息管理 | `message_manager.py` | 历史持久化 |
| 错误处理 | `exceptions.py` + `model_clients.py` | 自动重试 |
| 技能系统 | `skill_manager.py` | 按需加载 |

**代码统计**：
- 总行数：~2500 行
- 核心逻辑：~1500 行
- 工具实现：~1000 行

**适合人群**：
- 🎓 正在学习 LLM 应用开发
- 🔬 想研究 Agent 的内部机制
- 🏗️ 需要定制自己的 Agent 实现
- 🤔 对现有框架感到困惑或不满足

---

## 🚧 已知限制

1. **无流式输出**：模型响应需要等待完整返回
2. **无并发执行**：工具串行执行
3. **无持久记忆**：对话历史仅在内存中
4. **简单规划**：单轮 ReAct 循环

这些限制是**有意为之**，保持代码简洁易懂。可根据需要扩展。

---

## 🔮 扩展方向

- **流式输出**：添加 SSE 支持
- **并发执行**：异步工具调用
- **长期记忆**：集成向量数据库
- **多 Agent 协作**：Agent 间通信
- **Web UI**：Gradio/Streamlit 界面
- **工具市场**：共享工具库

---

**代码不多，但该有的都有。读一遍代码，胜过看十遍教程。** 🚀
