"""消息管理器 - 管理对话消息列表"""

from typing import Any


class MessageManager:
    """消息列表管理"""
    
    def __init__(self, system_prompt: str):
        self.messages: list[dict[str, str]] = []
        self._add_system(system_prompt)
    
    def _add_system(self, content: str) -> None:
        """添加系统消息"""
        self.messages.append({"role": "system", "content": content})
    
    def add_user(self, content: str) -> None:
        """添加用户消息"""
        self.messages.append({"role": "user", "content": content})
    
    def add_assistant(self, content: str) -> None:
        """添加助手消息"""
        self.messages.append({"role": "assistant", "content": content})
    
    def add_observation(self, content: str) -> None:
        """添加观察结果消息"""
        self.messages.append({"role": "user", "content": f"<observation>{content}</observation>"})
    
    def add_question(self, content: str) -> None:
        """添加问题消息"""
        self.messages.append({"role": "user", "content": f"<question>{content}</question>"})
    
    def get_last_assistant(self) -> str | None:
        """获取最后一条助手消息"""
        for msg in reversed(self.messages):
            if msg["role"] == "assistant":
                return msg["content"]
        return None
    
    def __len__(self) -> int:
        return len(self.messages)
    
    def __iter__(self):
        return iter(self.messages)
