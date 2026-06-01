"""ReAct Agent - 核心推理循环"""

import os
import platform
import re
from string import Template
from typing import Any, Callable

from reason_action_agent.config import AgentConfig, load_config
from reason_action_agent.exceptions import AgentException, ModelOutputError
from reason_action_agent.message_manager import MessageManager
from reason_action_agent.model_clients import create_model_client
from reason_action_agent.prompts import react_system_prompt_template
from reason_action_agent.rich_display import display
from reason_action_agent.session_exporter import SessionExporter
from reason_action_agent.session_logger import SessionLogger
from reason_action_agent.tag_parser import TagParser
from reason_action_agent.tools import ToolRegistry, get_default_tools


class ReActAgent:
    """ReAct Agent - 推理行动循环"""
    
    def __init__(
        self,
        tools: list[Callable] | None = None,
        config: AgentConfig | None = None,
        logger: SessionLogger | None = None,
    ):
        self.config = config or load_config()
        self.registry = self._init_tools(tools)
        self.model_client = create_model_client(
            self.config.model.protocol,
            self.config.model.name,
            self.config.model.base_url,
            self.config.model.api_key,
        )
        self.logger = logger or self._init_logger()
        self.parser = TagParser()
        self.exporter = SessionExporter(project_dir=self.config.project_directory)
        
        self._log("agent_initialized", {
            "model": self.config.model.name,
            "protocol": self.config.model.protocol,
            "project_directory": self.config.project_directory,
            "tools": [t.name for t in self.registry.list_tools()],
        })
    
    def _init_tools(self, tools: list[Callable] | None) -> ToolRegistry:
        """初始化工具注册器"""
        registry = ToolRegistry()
        for func in tools or get_default_tools():
            registry.register(func)
        return registry
    
    def _init_logger(self) -> SessionLogger | None:
        """初始化日志记录器"""
        if not self.config.log.enabled:
            return None
        return SessionLogger(log_dir=self.config.log.dir)
    
    def run(self, user_input: str) -> str:
        """执行推理循环"""
        # 清空导出器
        self.exporter.clear()
        self.exporter.add_user_input(user_input)
        
        # 初始化消息
        system_prompt = self._render_system_prompt()
        messages = MessageManager(system_prompt)
        messages.add_question(user_input)
        
        self._log("user_input", user_input)
        self._log_text("SYSTEM_PROMPT", system_prompt)
        
        # 推理循环
        while True:
            # 调用模型
            display.thinking()
            content = self._call_model(messages)
            
            # 提取思考
            if thought := self.parser.extract(content, "thought"):
                display.thought(thought)
                self.exporter.add_thought(thought)
                self._log("thought", thought)
            
            # 检查是否结束
            if final_answer := self.parser.extract(content, "final_answer"):
                display.final_answer(final_answer)
                self.exporter.add_final_answer(final_answer)
                self._log("final_answer", final_answer)
                return final_answer
            
            # 提取动作
            action = self.parser.extract(content, "action")
            if not action:
                # 模型输出格式异常，尝试智能修复
                error_msg = self._handle_invalid_output(content, messages)
                if error_msg:
                    # 添加错误提示，让模型重新输出
                    continue
            
            # 解析并执行动作
            try:
                tool_name, args, kwargs = self.parser.parse_action(action)
            except AgentException as e:
                raise ModelOutputError(f"Action 解析失败: {e}", content)
            
            display.action(tool_name, args, kwargs)
            self.exporter.add_action(tool_name, args, kwargs)
            self._log("action", {
                "raw": action,
                "formatted": self.parser.format_tool_call(tool_name, args, kwargs),
                "tool_name": tool_name,
                "args": args,
                "kwargs": kwargs,
            })
            
            # 安全确认
            if tool_name == "run_terminal_command":
                if not self._confirm_command():
                    display.warning("操作被用户取消")
                    self.exporter.add_error("操作被用户取消")
                    return "操作被用户取消"
            
            # 执行工具
            observation = self._execute_tool(tool_name, args, kwargs)
            display.observation(observation)
            self.exporter.add_observation(observation)
            
            # 添加观察结果
            messages.add_observation(observation)
            self._log("observation", {"tool_name": tool_name, "observation": observation})
    
    def _confirm_command(self) -> bool:
        """确认是否执行终端命令"""
        display.warning("即将执行终端命令，请确认！")
        should_continue = display.console.input("\n[yellow]是否继续？(Y/N): [/yellow]").lower()
        self._log("terminal_command_confirmation", should_continue)
        return should_continue == "y"
    
    def _execute_tool(self, name: str, args: list, kwargs: dict) -> str:
        """执行工具"""
        if not self.registry.has(name):
            self._log("tool_not_found", {"tool_name": name})
            return f"工具不存在：{name}"
        
        try:
            return self.registry.execute(name, args, kwargs)
        except Exception as e:
            self._log("tool_error", {"tool_name": name, "error": str(e)})
            return f"工具执行错误：{e}"
    
    def _call_model(self, messages: MessageManager) -> str:
        """调用模型"""
        print("\n\n正在请求模型，请稍等...")
        msg_list = list(messages)
        self._log("model_request", msg_list)
        
        content = self.model_client.call(msg_list)
        messages.add_assistant(content)
        
        self._log_text("MODEL_RAW_OUTPUT", content)
        return content
    
    def _render_system_prompt(self) -> str:
        """渲染系统提示"""
        file_list = self._get_file_list()
        return Template(react_system_prompt_template).substitute(
            operating_system=self._get_os_name(),
            tool_list=self.registry.format_tool_list(),
            file_list=file_list,
        )
    
    def _get_file_list(self) -> str:
        """获取项目文件列表"""
        if not self.config.project_directory:
            return ""
        return ", ".join(
            os.path.abspath(os.path.join(self.config.project_directory, filename))
            for filename in os.listdir(self.config.project_directory)
        )
    
    @staticmethod
    def _get_os_name() -> str:
        """获取操作系统名称"""
        return {
            "Darwin": "macOS",
            "Windows": "Windows",
            "Linux": "Linux",
        }.get(platform.system(), "Unknown")
    
    def _handle_invalid_output(self, content: str, messages: MessageManager) -> str | None:
        """处理模型输出格式异常"""
        self._log("invalid_model_output", {"content": content})
        
        # 显示原始输出（截断）
        truncated = content[:500] + ("..." if len(content) > 500 else "")
        display.warning("模型输出格式异常")
        display.code(truncated, language="text")
        
        # 尝试智能修复常见问题
        fixed_content = self._try_fix_output(content)
        if fixed_content:
            display.info("尝试自动修复...")
            # 移除错误的助手消息
            messages.messages.pop()  # 移除刚才添加的错误消息
            # 添加修复后的消息
            messages.add_assistant(fixed_content)
            return None  # 继续循环处理修复后的内容
        
        # 无法自动修复，添加提示让模型重新输出
        error_hint = """
<observation>
【系统提示】你的输出格式不正确。

请严格按照以下格式输出：
1. 必须包含 <thought> 标签说明你的思考
2. 如果需要调用工具，必须输出 <action> 标签
3. 如果可以直接回答，必须输出 <final_answer> 标签

正确示例：
<thought>我需要先读取文件内容</thought>
<action>read_file("/path/to/file")</action>

或者直接回答：
<thought>这是简单问题，可以直接回答</thought>
<final_answer>答案是...</final_answer>
</observation>
"""
        messages.add_user(error_hint)
        return error_hint
    
    def _try_fix_output(self, content: str) -> str | None:
        """尝试修复常见的输出格式问题"""
        # 问题1：有 thought 但缺少 action/final_answer 标签
        if "<thought>" in content and "</thought>" in content:
            thought = self.parser.extract(content, "thought")
            if not thought:
                return None
            
            # 检查是否有未包裹在标签中的代码
            code_match = self._extract_code_like_action(content)
            if code_match:
                return f"<thought>{thought}</thought>\n<action>{code_match}</action>"
            
            # 检查是否有未包裹在标签中的答案
            answer_match = self._extract_answer_like_content(content)
            if answer_match:
                return f"<thought>{thought}</thought>\n<final_answer>{answer_match}</final_answer>"
        
        # 问题2：直接输出了函数调用但没有 action 标签
        if "(" in content and ")" in content and "def " not in content:
            # 尝试提取看起来像函数调用的内容
            import re
            func_pattern = r'(\w+\([^)]+\))'
            match = re.search(func_pattern, content)
            if match:
                action = match.group(1)
                return f"<thought>执行工具调用</thought>\n<action>{action}</action>"
        
        return None
    
    def _extract_code_like_action(self, content: str) -> str | None:
        """提取看起来像工具调用的代码"""
        import re
        # 匹配函数调用模式
        pattern = r'(\w+)\s*\([^)]*\)'
        matches = re.findall(pattern, content)
        
        for match in matches:
            # 检查是否是已注册的工具
            if self.registry.has(match):
                # 提取完整调用
                full_pattern = rf'{match}\s*\([^)]*\)'
                full_match = re.search(full_pattern, content)
                if full_match:
                    return full_match.group(0)
        
        return None
    
    def _extract_answer_like_content(self, content: str) -> str | None:
        """提取看起来像答案的内容"""
        # 移除已有的标签
        import re
        cleaned = re.sub(r'<[^>]+>.*?</[^>]+>', '', content, flags=re.DOTALL)
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        cleaned = cleaned.strip()
        
        if len(cleaned) > 10:  # 有实质内容
            return cleaned[:500]  # 限制长度
        
        return None
    
    def _log(self, event: str, data: Any = None) -> None:
        """记录日志"""
        if self.logger:
            self.logger.log(event, data)
    
    def _log_text(self, title: str, text: str) -> None:
        """记录文本日志"""
        if self.logger:
            self.logger.log_text(title, text)
