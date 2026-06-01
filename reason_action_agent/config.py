"""配置管理模块 - 统一管理环境变量和默认配置"""

import os
from dataclasses import dataclass, field
from typing import Literal

from dotenv import load_dotenv


@dataclass
class ModelConfig:
    """模型配置"""
    protocol: Literal["openai", "anthropic"] = "openai"
    name: str = ""
    base_url: str = ""
    api_key: str = ""
    max_tokens: int = 4096


@dataclass
class LogConfig:
    """日志配置"""
    dir: str = "logs"
    enabled: bool = True


@dataclass
class AgentConfig:
    """Agent 总配置"""
    model: ModelConfig = field(default_factory=ModelConfig)
    log: LogConfig = field(default_factory=LogConfig)
    project_directory: str = ""


# 默认配置
DEFAULTS = {
    "openai": {
        "base_url": "https://oneapi-comate.baidu-int.com/v1",
        "model": "deepseek-v4-flash",
    },
    "anthropic": {
        "base_url": "https://oneapi-comate.baidu-int.com",
        "model": "Claude Sonnet 4.6",
        "max_tokens": 4096,
    },
}


def load_config() -> AgentConfig:
    """从环境变量加载配置"""
    load_dotenv()
    
    protocol = os.getenv("MODEL_PROTOCOL", "openai").lower()
    if protocol not in DEFAULTS:
        raise ValueError(f"不支持的协议：{protocol}")
    
    defaults = DEFAULTS[protocol]
    
    model_config = ModelConfig(
        protocol=protocol,
        name=os.getenv(f"{protocol.upper()}_MODEL", defaults["model"]),
        base_url=os.getenv(f"{protocol.upper()}_BASE_URL", defaults["base_url"]),
        api_key=_get_api_key(protocol),
        max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", defaults.get("max_tokens", 4096))),
    )
    
    log_config = LogConfig(
        dir=os.getenv("AGENT_LOG_DIR", "logs"),
        enabled=os.getenv("AGENT_LOG_ENABLED", "true").lower() == "true",
    )
    
    return AgentConfig(
        model=model_config,
        log=log_config,
    )


def _get_api_key(protocol: str) -> str:
    """获取 API Key"""
    # 优先使用 ONEAPI_API_KEY
    api_key = os.getenv("ONEAPI_API_KEY")
    
    # 如果没有，尝试协议特定的环境变量
    if not api_key:
        env_name = f"{protocol.upper()}_API_KEY"
        api_key = os.getenv(env_name)
    
    if not api_key:
        raise ValueError(f"未找到 ONEAPI_API_KEY 或 {protocol.upper()}_API_KEY 环境变量，请在 .env 文件中设置。")
    
    return api_key
