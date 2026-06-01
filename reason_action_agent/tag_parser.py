"""标签解析器 - 解析模型输出的 XML 标签"""

import ast
import re
from typing import Any

from reason_action_agent.exceptions import ActionParseError


class TagParser:
    """XML 标签解析器"""
    
    @staticmethod
    def extract(content: str, tag: str) -> str | None:
        """提取标签内容"""
        match = re.search(rf"<{tag}>(.*?)</{tag}>", content, re.DOTALL)
        return match.group(1).strip() if match else None
    
    @staticmethod
    def parse_action(code_str: str) -> tuple[str, list[Any], dict[str, Any]]:
        """解析 Action 为工具名、位置参数、关键字参数"""
        try:
            expression = ast.parse(code_str.strip(), mode="eval").body
            if not isinstance(expression, ast.Call):
                raise ActionParseError(code_str, "不是有效的函数调用")
            if not isinstance(expression.func, ast.Name):
                raise ActionParseError(code_str, "无法识别函数名")
            
            tool_name = expression.func.id
            args = [ast.literal_eval(arg) for arg in expression.args]
            kwargs = {
                keyword.arg: ast.literal_eval(keyword.value)
                for keyword in expression.keywords
            }
            return tool_name, args, kwargs
        except (SyntaxError, ValueError) as e:
            raise ActionParseError(code_str, str(e))
    
    @staticmethod
    def format_tool_call(tool_name: str, args: list, kwargs: dict) -> str:
        """格式化工具调用显示"""
        values = [repr(arg) for arg in args]
        values.extend(f"{key}={value!r}" for key, value in kwargs.items())
        return f"{tool_name}({', '.join(values)})"
