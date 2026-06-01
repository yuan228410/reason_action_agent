"""主题配置 - 支持多种颜色主题"""

from rich.theme import Theme
from typing import Dict


# 预定义主题
THEMES: Dict[str, Theme] = {
    "default": Theme({
        "thought": "bold cyan",
        "action": "bold yellow",
        "observation": "bold green",
        "answer": "bold magenta",
        "error": "bold red",
        "info": "bold blue",
        "warning": "bold yellow",
        "tool_name": "cyan",
        "tool_args": "yellow",
        "code": "green",
        "file_path": "blue underline",
        "line_number": "dim",
        "directory": "bold yellow",
        "file": "green",
        "match": "bold red",
    }),
    
    "dark": Theme({
        "thought": "bold bright_cyan",
        "action": "bold bright_yellow",
        "observation": "bold bright_green",
        "answer": "bold bright_magenta",
        "error": "bold bright_red",
        "info": "bold bright_blue",
        "warning": "bold bright_yellow",
        "tool_name": "bright_cyan",
        "tool_args": "bright_yellow",
        "code": "bright_green",
        "file_path": "bright_blue underline",
        "line_number": "bright_black",
        "directory": "bold bright_yellow",
        "file": "bright_green",
        "match": "bold bright_red",
    }),
    
    "light": Theme({
        "thought": "bold #008b8b",  # dark cyan
        "action": "bold #8b8b00",  # dark yellow
        "observation": "bold #006400",  # dark green
        "answer": "bold #8b008b",  # dark magenta
        "error": "bold #8b0000",  # dark red
        "info": "bold #00008b",  # dark blue
        "warning": "bold #8b8b00",
        "tool_name": "#008b8b",
        "tool_args": "#8b8b00",
        "code": "#006400",
        "file_path": "#00008b underline",
        "line_number": "#7f7f7f",  # grey50
        "directory": "bold #8b8b00",
        "file": "#006400",
        "match": "bold #8b0000",
    }),
    
    "monokai": Theme({
        "thought": "bold #66d9ef",  # cyan
        "action": "bold #f8f8f2",  # white
        "observation": "bold #a6e22e",  # green
        "answer": "bold #ae81ff",  # purple
        "error": "bold #f92672",  # red
        "info": "bold #66d9ef",
        "warning": "bold #fd971f",  # orange
        "tool_name": "#66d9ef",
        "tool_args": "#e6db74",  # yellow
        "code": "#a6e22e",
        "file_path": "#75715e underline",  # comment gray
        "line_number": "#75715e",
        "directory": "bold #fd971f",
        "file": "#a6e22e",
        "match": "bold #f92672",
    }),
    
    "ocean": Theme({
        "thought": "bold #00afff",  # deep blue
        "action": "bold #00ffff",  # cyan
        "observation": "bold #5fd700",  # sea green
        "answer": "bold #d787ff",  # lavender
        "error": "bold #ff5f5f",  # coral red
        "info": "bold #00afff",
        "warning": "bold #ffd700",  # gold
        "tool_name": "#00afff",
        "tool_args": "#87d7ff",  # light blue
        "code": "#5fd700",
        "file_path": "#87afff underline",
        "line_number": "#5f87af",
        "directory": "bold #00ffff",
        "file": "#5fd700",
        "match": "bold #ff5f5f",
    }),
    
    "solarized": Theme({
        "thought": "bold #2aa198",  # cyan
        "action": "bold #b58900",  # yellow
        "observation": "bold #859900",  # green
        "answer": "bold #d33682",  # magenta
        "error": "bold #dc322f",  # red
        "info": "bold #268bd2",  # blue
        "warning": "bold #cb4b16",  # orange
        "tool_name": "#2aa198",
        "tool_args": "#b58900",
        "code": "#859900",
        "file_path": "#268bd2 underline",
        "line_number": "#657b83",  # base00
        "directory": "bold #b58900",
        "file": "#859900",
        "match": "bold #dc322f",
    }),
}


def get_theme(name: str) -> Theme:
    """获取主题"""
    if name not in THEMES:
        from reason_action_agent.rich_display import display
        display.warning(f"主题 '{name}' 不存在，使用默认主题")
        return THEMES["default"]
    return THEMES[name]


def list_themes() -> list:
    """列出所有主题"""
    return list(THEMES.keys())


def get_theme_info() -> str:
    """获取主题信息"""
    info = """可用主题:

  [cyan]default[/cyan]     - 默认主题（经典配色）
  [cyan]dark[/cyan]        - 暗色主题（高对比度）
  [cyan]light[/cyan]       - 亮色主题（适合浅色终端）
  [cyan]monokai[/cyan]     - Monokai 风格（类似 Sublime）
  [cyan]ocean[/cyan]       - 海洋主题（蓝色系）
  [cyan]solarized[/cyan]   - Solarized 配色

使用方法: theme <主题名>
示例: theme monokai
"""
    return info
