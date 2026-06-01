"""模型客户端 - OpenAI 和 Anthropic（带错误处理）"""

import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anthropic import Anthropic
    from openai import OpenAI

from rich.progress import Progress, SpinnerColumn, TextColumn

from reason_action_agent.rich_display import display
from reason_action_agent.exceptions import ModelCallError, NetworkError, RateLimitError, TimeoutError


class ModelClient(ABC):
    """模型客户端基类"""
    
    def __init__(self, model: str, max_retries: int = 3, retry_delay: int = 2):
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    @abstractmethod
    def call(self, messages: list[dict[str, str]]) -> str:
        """调用模型"""
        pass
    
    def _handle_error(self, error: Exception, operation: str = "调用模型") -> str:
        """处理错误，返回用户友好的错误消息"""
        error_msg = str(error)
        
        # 网络错误
        if "ChunkedEncodingError" in error_msg or "ConnectionError" in error_msg:
            return f"❌ 网络连接中断，请检查网络后重试"
        
        # 限流错误
        if "429" in error_msg or "rate limit" in error_msg.lower():
            return f"⚠️  请求过于频繁，请稍后再试"
        
        # 超时
        if "timeout" in error_msg.lower():
            return f"⚠️  请求超时，请稍后重试"
        
        # API 错误
        if "401" in error_msg or "Unauthorized" in error_msg:
            return f"❌ API Key 无效，请检查配置"
        
        if "403" in error_msg:
            return f"❌ 无权限访问该模型"
        
        if "404" in error_msg:
            return f"❌ 模型不存在或未启用"
        
        # 其他错误
        return f"❌ {operation}失败: {error_msg}"


class OpenAIModelClient(ModelClient):
    """OpenAI 协议客户端"""
    
    def __init__(self, model: str, base_url: str, api_key: str, max_retries: int = 3, retry_delay: int = 2):
        super().__init__(model, max_retries, retry_delay)
        # 延迟导入
        from openai import OpenAI
        self.client = OpenAI(base_url=base_url, api_key=api_key)
    
    def call(self, messages: list[dict[str, str]]) -> str:
        """调用模型（带重试）"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=display.console,
                    transient=True,
                ) as progress:
                    task_desc = f"[cyan]调用模型 {self.model}"
                    if attempt > 0:
                        task_desc += f" (重试 {attempt + 1}/{self.max_retries})"
                    progress.add_task(task_desc, total=None)
                    
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                    )
                    return response.choices[0].message.content
                    
            except Exception as e:
                last_error = e
                
                # 检查是否需要重试
                error_msg = str(e)
                should_retry = (
                    "ChunkedEncodingError" in error_msg or
                    "ConnectionError" in error_msg or
                    "timeout" in error_msg.lower() or
                    "429" in error_msg
                )
                
                if should_retry and attempt < self.max_retries - 1:
                    # 显示重试提示
                    display.warning(f"模型调用失败，{self.retry_delay}秒后重试...")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    # 不重试或已达到最大重试次数
                    break
        
        # 所有重试都失败了
        error_msg = self._handle_error(last_error)
        raise ModelCallError(error_msg, last_error)


class AnthropicModelClient(ModelClient):
    """Anthropic 协议客户端"""
    
    def __init__(self, model: str, base_url: str, api_key: str, max_tokens: int = 4096, max_retries: int = 3, retry_delay: int = 2):
        super().__init__(model, max_retries, retry_delay)
        self.max_tokens = max_tokens
        # 延迟导入
        from anthropic import Anthropic
        self.client = Anthropic(base_url=base_url, api_key=api_key)
    
    def call(self, messages: list[dict[str, str]]) -> str:
        """调用模型（带重试）"""
        system_prompt = messages[0]["content"]
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=display.console,
                    transient=True,
                ) as progress:
                    task_desc = f"[cyan]调用模型 {self.model}"
                    if attempt > 0:
                        task_desc += f" (重试 {attempt + 1}/{self.max_retries})"
                    progress.add_task(task_desc, total=None)
                    
                    response = self.client.messages.create(
                        model=self.model,
                        max_tokens=self.max_tokens,
                        system=system_prompt,
                        messages=messages[1:],
                    )
                    return "".join(block.text for block in response.content if block.type == "text")
                    
            except Exception as e:
                last_error = e
                
                # 检查是否需要重试
                error_msg = str(e)
                should_retry = (
                    "ChunkedEncodingError" in error_msg or
                    "ConnectionError" in error_msg or
                    "timeout" in error_msg.lower() or
                    "429" in error_msg
                )
                
                if should_retry and attempt < self.max_retries - 1:
                    display.warning(f"模型调用失败，{self.retry_delay}秒后重试...")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    break
        
        # 所有重试都失败了
        error_msg = self._handle_error(last_error)
        raise ModelCallError(error_msg, last_error)


def create_model_client(protocol: str, model: str, base_url: str, api_key: str) -> ModelClient:
    """创建模型客户端"""
    if protocol == "openai":
        return OpenAIModelClient(model, base_url, api_key)
    if protocol == "anthropic":
        return AnthropicModelClient(model, base_url, api_key)
    raise ValueError(f"不支持的协议：{protocol}")
