"""工具注册器 - 支持动态注册和工具发现"""

import inspect
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Tool:
    """工具定义"""
    name: str
    func: Callable
    description: str = ""
    signature: str = ""
    
    def __post_init__(self):
        if not self.description:
            self.description = inspect.getdoc(self.func) or ""
        if not self.signature:
            self.signature = str(inspect.signature(self.func))
    
    def call(self, *args, **kwargs) -> Any:
        """执行工具"""
        return self.func(*args, **kwargs)
    
    def format_call(self, args: list, kwargs: dict) -> str:
        """格式化工具调用"""
        values = [repr(arg) for arg in args]
        values.extend(f"{key}={value!r}" for key, value in kwargs.items())
        return f"{self.name}({', '.join(values)})"
    
    def __str__(self) -> str:
        return f"- {self.name}{self.signature}: {self.description}"


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    
    def register(self, func: Callable | None = None, *, name: str | None = None) -> Callable:
        """注册工具（支持装饰器用法）"""
        def decorator(f: Callable) -> Callable:
            tool_name = name or f.__name__
            self._tools[tool_name] = Tool(name=tool_name, func=f)
            return f
        
        if func is not None:
            return decorator(func)
        return decorator
    
    def get(self, name: str) -> Tool | None:
        """获取工具"""
        return self._tools.get(name)
    
    def has(self, name: str) -> bool:
        """检查工具是否存在"""
        return name in self._tools
    
    def list_tools(self) -> list[Tool]:
        """获取所有工具"""
        return list(self._tools.values())
    
    def format_tool_list(self) -> str:
        """生成工具列表字符串"""
        return "\n".join(str(tool) for tool in self._tools.values())
    
    def execute(self, name: str, args: list, kwargs: dict) -> Any:
        """执行工具"""
        tool = self.get(name)
        if not tool:
            raise ToolNotFoundError(f"工具不存在：{name}")
        return tool.call(*args, **kwargs)


class ToolNotFoundError(Exception):
    """工具未找到异常"""
    pass


# 全局注册器
_registry = ToolRegistry()


def tool(func: Callable | None = None, *, name: str | None = None) -> Callable:
    """工具注册装饰器"""
    return _registry.register(func, name=name)


def get_registry() -> ToolRegistry:
    """获取全局工具注册器"""
    return _registry
