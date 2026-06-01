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


class ModelCallError(AgentException):
    """模型调用错误"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.original_error = original_error
        super().__init__(message)


class SkillError(AgentException):
    """技能相关错误"""
    def __init__(self, skill_name: str, operation: str, error: Exception):
        self.skill_name = skill_name
        self.operation = operation
        self.error = error
        super().__init__(f"技能 {skill_name} {operation} 失败: {error}")


class NetworkError(AgentException):
    """网络错误"""
    def __init__(self, operation: str, error: Exception):
        self.operation = operation
        self.error = error
        super().__init__(f"网络请求失败 ({operation}): {error}")


class RateLimitError(AgentException):
    """限流错误"""
    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(f"请求被限流，请在 {retry_after} 秒后重试")


class TimeoutError(AgentException):
    """超时错误"""
    def __init__(self, operation: str, timeout: int):
        self.operation = operation
        self.timeout = timeout
        super().__init__(f"{operation} 超时 ({timeout}秒)")

