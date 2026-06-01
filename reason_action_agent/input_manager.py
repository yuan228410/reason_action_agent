"""输入管理器 - 支持斜杠命令和自动补全"""

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from pathlib import Path
from typing import List, Dict


class CommandCompleter(Completer):
    """命令自动补全"""
    
    def __init__(self):
        # 命令列表：命令 -> (描述, 参数提示)
        self.commands: Dict[str, tuple] = {
            "/help": ("显示帮助信息", ""),
            "/tools": ("查看工具列表", ""),
            "/themes": ("查看主题列表", ""),
            "/theme": ("切换主题", "<主题名>"),
            "/export": ("导出会话", "md|html"),
            "/stats": ("查看执行统计", ""),
            "/clear": ("清空对话历史并清屏", ""),
            "/cls": ("仅清屏", ""),
            "/quit": ("退出程序", ""),
            "/q": ("退出程序（简写）", ""),
        }
    
    def get_completions(self, document, complete_event):
        """获取补全建议"""
        text = document.text_before_cursor
        
        # 只对斜杠命令补全
        if text.startswith("/"):
            # 提取命令部分
            parts = text.split()
            if len(parts) == 1:
                # 补全命令名
                for cmd, (desc, args) in self.commands.items():
                    if cmd.startswith(text):
                        yield Completion(
                            cmd,
                            start_position=-len(text),
                            display=f"{cmd}",
                            display_meta=desc,
                        )
            
            elif len(parts) == 2:
                # 补全命令参数
                cmd = parts[0]
                partial = parts[1]
                
                # theme 命令补全主题名
                if cmd == "/theme":
                    themes = ["default", "dark", "light", "monokai", "ocean", "solarized"]
                    for theme in themes:
                        if theme.startswith(partial):
                            yield Completion(
                                theme,
                                start_position=-len(partial),
                                display=theme,
                                display_meta="主题",
                            )
                
                # export 命令补全格式
                elif cmd == "/export":
                    formats = ["md", "html"]
                    for fmt in formats:
                        if fmt.startswith(partial):
                            yield Completion(
                                fmt,
                                start_position=-len(partial),
                                display=fmt,
                                display_meta="导出格式",
                            )


class InputManager:
    """输入管理器"""
    
    def __init__(self, history_file: str = ".agent_history"):
        self.history_file = Path.home() / history_file
        self.session = PromptSession(
            history=FileHistory(str(self.history_file)),
            completer=CommandCompleter(),
            complete_while_typing=True,
        )
        
        # 自定义样式
        self.style = Style.from_dict({
            "prompt": "bold cyan",
            "completion": "bg:#333333 #ffffff",
            "completion.selected": "bg:#00aa00 #ffffff",
            "scrollbar": "bg:#444444",
            "scrollbar.button": "bg:#888888",
        })
    
    def get_input(self, prompt_text: str = "💬 请输入任务") -> str:
        """获取用户输入"""
        try:
            result = self.session.prompt(
                f"{prompt_text}: ",
                style=self.style,
            )
            # 确保 result 不为 None
            return (result or "").strip()
        except KeyboardInterrupt:
            # Ctrl+C 返回特殊标记
            return "__CTRL_C__"
        except EOFError:
            # Ctrl+D 返回 quit
            return "/quit"
    
    def is_command(self, text: str) -> bool:
        """判断是否为命令"""
        return text.startswith("/")
    
    def parse_command(self, text: str) -> tuple:
        """解析命令，返回 (命令名, 参数)"""
        if not self.is_command(text):
            return None, None
        
        parts = text.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        return cmd, args
    
    def get_command_help(self, cmd: str) -> str:
        """获取命令帮助"""
        completer = CommandCompleter()
        if cmd in completer.commands:
            desc, args = completer.commands[cmd]
            if args:
                return f"{cmd} {args}\n  {desc}"
            return f"{cmd}\n  {desc}"
        return f"未知命令: {cmd}"
