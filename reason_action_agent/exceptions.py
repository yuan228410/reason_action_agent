"""异常定义"""

from typing import Optional


class AgentException(Exception):
    """Agent 基础异常"""
    pass


class ModelOutputError(AgentException):
    """模型输出格式错误"""
    def __init__(self, message: str, raw_output: Optional[str] = None):
        self.raw_output = raw_output
        # 增强错误信息
        if raw_output:
            preview = raw_output[:200] + ("..." if len(raw_output) > 200 else "")
            message = f"{message}\n\n原始输出预览:\n{preview}"
        super().__init__(message)


class ToolExecutionError(AgentException):
    """工具执行错误"""
    def __init__(self, tool_name: str, error: Exception):
        self.tool_name = tool_name
        self.error = error
        super().__init__(f"工具 {tool_name} 执行失败: {error}")


class ActionParseError(AgentException):
    """Action 解析错误"""
    def __init__(self, action_str: str, reason: str):
        self.action_str = action_str
        super().__init__(f"无法解析 Action: {reason}\n原始内容: {action_str}")


class ConfigurationError(AgentException):
    """配置错误"""
    pass
