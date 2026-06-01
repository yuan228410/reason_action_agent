"""系统工具"""

import os
from datetime import datetime
from typing import Optional

from reason_action_agent.tools.registry import tool


@tool
def current_time(timezone: Optional[str] = None) -> str:
    """
    获取当前时间
    
    Args:
        timezone: 时区（如 'Asia/Shanghai'），不传则使用系统时区
    
    Returns:
        格式化的当前时间
    """
    try:
        now = datetime.now()
        
        if timezone:
            from zoneinfo import ZoneInfo
            try:
                tz = ZoneInfo(timezone)
                now = datetime.now(tz)
            except Exception as e:
                return f"错误：无效的时区 '{timezone}'\n常用时区: Asia/Shanghai, America/New_York, Europe/London, UTC"
        
        return now.strftime("%Y-%m-%d %H:%M:%S %A")
    
    except Exception as e:
        return f"获取时间失败: {e}"


@tool
def get_env(name: str, default: Optional[str] = None) -> str:
    """
    获取环境变量
    
    Args:
        name: 环境变量名
        default: 默认值（变量不存在时返回）
    
    Returns:
        环境变量值
    """
    value = os.getenv(name, default)
    
    if value is None:
        return f"环境变量 '{name}' 不存在，且未提供默认值"
    
    return f"{name}={value}"


@tool
def set_env(name: str, value: str) -> str:
    """
    设置环境变量（仅当前进程有效）
    
    Args:
        name: 环境变量名
        value: 环境变量值
    
    Returns:
        操作结果
    """
    os.environ[name] = value
    return f"✓ 已设置环境变量: {name}={value}"


@tool
def list_env(pattern: Optional[str] = None) -> str:
    """
    列出环境变量
    
    Args:
        pattern: 过滤模式（可选），如 'PATH'
    
    Returns:
        环境变量列表
    """
    items = []
    
    for key, value in sorted(os.environ.items()):
        if pattern and pattern.lower() not in key.lower():
            continue
        items.append(f"{key}={value}")
    
    if not items:
        return f"未找到匹配 '{pattern}' 的环境变量"
    
    return "\n".join(items)


@tool
def get_system_info() -> str:
    """
    获取系统信息
    
    Returns:
        操作系统、Python 版本等信息
    """
    import platform
    import sys
    
    info = {
        "操作系统": platform.system(),
        "系统版本": platform.version(),
        "架构": platform.machine(),
        "主机名": platform.node(),
        "Python 版本": sys.version.split()[0],
        "Python 路径": sys.executable,
        "工作目录": os.getcwd(),
        "用户": os.getenv("USER", os.getenv("USERNAME", "未知")),
    }
    
    lines = ["🖥️  系统信息", "=" * 50]
    for key, value in info.items():
        lines.append(f"{key:12s}: {value}")
    
    return "\n".join(lines)
