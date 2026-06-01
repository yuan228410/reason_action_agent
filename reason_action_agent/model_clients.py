"""模型客户端 - OpenAI 和 Anthropic"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anthropic import Anthropic
    from openai import OpenAI

from rich.progress import Progress, SpinnerColumn, TextColumn

from reason_action_agent.rich_display import display


class ModelClient(ABC):
    """模型客户端基类"""
    
    def __init__(self, model: str):
        self.model = model
    
    @abstractmethod
    def call(self, messages: list[dict[str, str]]) -> str:
        """调用模型"""
        pass


class OpenAIModelClient(ModelClient):
    """OpenAI 协议客户端"""
    
    def __init__(self, model: str, base_url: str, api_key: str):
        super().__init__(model)
        # 延迟导入
        from openai import OpenAI
        self.client = OpenAI(base_url=base_url, api_key=api_key)
    
    def call(self, messages: list[dict[str, str]]) -> str:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=display.console,
            transient=True,  # 完成后自动消失
        ) as progress:
            progress.add_task(f"[cyan]调用模型 {self.model}...", total=None)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content


class AnthropicModelClient(ModelClient):
    """Anthropic 协议客户端"""
    
    def __init__(self, model: str, base_url: str, api_key: str, max_tokens: int = 4096):
        super().__init__(model)
        self.max_tokens = max_tokens
        # 延迟导入
        from anthropic import Anthropic
        self.client = Anthropic(base_url=base_url, api_key=api_key)
    
    def call(self, messages: list[dict[str, str]]) -> str:
        system_prompt = messages[0]["content"]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=display.console,
            transient=True,
        ) as progress:
            progress.add_task(f"[cyan]调用模型 {self.model}...", total=None)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=messages[1:],
            )
            return "".join(block.text for block in response.content if block.type == "text")


def create_model_client(protocol: str, model: str, base_url: str, api_key: str) -> ModelClient:
    """创建模型客户端"""
    if protocol == "openai":
        return OpenAIModelClient(model, base_url, api_key)
    if protocol == "anthropic":
        return AnthropicModelClient(model, base_url, api_key)
    raise ValueError(f"不支持的协议：{protocol}")
