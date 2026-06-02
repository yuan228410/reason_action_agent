"""输入管理器 - 支持斜杠命令和自动补全"""

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from pathlib import Path
from typing import List, Dict


class CommandCompleter(Completer):
    """命令自动补全"""
    
    def __init__(self, project_dir: str = None):
        # 保存项目目录
        self.project_dir = project_dir
        
        # 命令列表：命令 -> (描述, 参数提示)
        self.commands: Dict[str, tuple] = {
            "/help": ("显示帮助信息", ""),
            "/tools": ("查看工具列表", ""),
            "/skills": ("查看技能列表", ""),
            "/skill": ("技能管理", "install|load|info|create|run|read|uninstall"),
            "/themes": ("查看主题列表", ""),
            "/theme": ("切换主题", "<主题名>"),
            "/export": ("导出会话", "md|html"),
            "/stats": ("查看执行统计", ""),
            "/clear": ("清空对话历史并清屏", ""),
            "/cls": ("仅清屏", ""),
            "/quit": ("退出程序", ""),
            "/q": ("退出程序（简写）", ""),
        }
        
        # skill 子命令列表（需要技能名作为参数的）
        self.skill_name_commands = ["load", "info", "run", "read", "uninstall"]
        # 所有 skill 子命令
        self.skill_subcommands = ["install", "load", "info", "create", "run", "read", "uninstall"]
    
    def _get_skill_names(self):
        """动态获取技能名称列表"""
        try:
            from reason_action_agent.skill_manager import SkillManager
            # 传入工作空间目录，加载项目级技能
            manager = SkillManager(project_dir=self.project_dir)
            skills = manager.list_skills()
            return [(skill.name, skill.metadata.version) for skill in skills]
        except Exception:
            return []
    
    def get_completions(self, document, complete_event):
        """获取补全建议 - 支持多级补全"""
        text = document.text_before_cursor
        
        # 只对斜杠命令补全
        if not text.startswith("/"):
            return
        
        # 检查文本末尾是否有空格（表示要补全下一级）
        text_ends_with_space = text.endswith(" ")
        
        # 分割命令（忽略末尾空格）
        parts = text.strip().split()
        
        # 第一级：补全命令名
        if len(parts) == 0 or (len(parts) == 1 and not text_ends_with_space):
            partial = parts[0] if parts else ""
            for cmd, (desc, args) in self.commands.items():
                if cmd.startswith(partial):
                    yield Completion(
                        cmd,
                        start_position=-len(partial),
                        display=cmd,
                        display_meta=desc,
                    )
        
        # 第二级：补全命令参数或子命令
        elif len(parts) == 1 and text_ends_with_space:
            cmd = parts[0]
            # /theme 命令补全主题名
            if cmd == "/theme":
                for theme in ["default", "dark", "light", "monokai", "ocean", "solarized"]:
                    yield Completion(
                        theme,
                        start_position=0,
                        display=theme,
                        display_meta="主题",
                    )
            
            # /export 命令补全格式
            elif cmd == "/export":
                for fmt in ["md", "html"]:
                    yield Completion(
                        fmt,
                        start_position=0,
                        display=fmt,
                        display_meta="导出格式",
                    )
            
            # /skill 命令补全子命令
            elif cmd == "/skill":
                for subcmd in self.skill_subcommands:
                    yield Completion(
                        subcmd,
                        start_position=0,
                        display=subcmd,
                        display_meta="子命令",
                    )
        
        # 第二级（已输入部分字符）：补全参数
        elif len(parts) == 2 and not text_ends_with_space:
            cmd = parts[0]
            partial = parts[1]
            
            # /theme 命令补全主题名
            if cmd == "/theme":
                for theme in ["default", "dark", "light", "monokai", "ocean", "solarized"]:
                    if theme.startswith(partial):
                        yield Completion(
                            theme,
                            start_position=-len(partial),
                            display=theme,
                            display_meta="主题",
                        )
            
            # /export 命令补全格式
            elif cmd == "/export":
                for fmt in ["md", "html"]:
                    if fmt.startswith(partial):
                        yield Completion(
                            fmt,
                            start_position=-len(partial),
                            display=fmt,
                            display_meta="导出格式",
                        )
            
            # /skill 命令补全子命令
            elif cmd == "/skill":
                for subcmd in self.skill_subcommands:
                    if subcmd.startswith(partial):
                        yield Completion(
                            subcmd,
                            start_position=-len(partial),
                            display=subcmd,
                            display_meta="子命令",
                        )
        
        # 第三级：补全技能名（/skill load/info/run/read/uninstall 后）
        elif len(parts) == 2 and text_ends_with_space:
            cmd = parts[0]
            subcmd = parts[1]
            
            if cmd == "/skill" and subcmd in self.skill_name_commands:
                for skill_name, skill_version in self._get_skill_names():
                    yield Completion(
                        skill_name,
                        start_position=0,
                        display=skill_name,
                        display_meta=f"技能 (v{skill_version})",
                    )
        
        # 第三级（已输入部分字符）：补全技能名
        elif len(parts) >= 3 and not text_ends_with_space:
            cmd = parts[0]
            subcmd = parts[1] if len(parts) > 1 else ""
            partial = parts[-1]
            
            if cmd == "/skill" and subcmd in self.skill_name_commands:
                for skill_name, skill_version in self._get_skill_names():
                    if skill_name.startswith(partial):
                        yield Completion(
                            skill_name,
                            start_position=-len(partial),
                            display=skill_name,
                            display_meta=f"技能 (v{skill_version})",
                        )


class InputManager:
    """输入管理器"""
    
    def __init__(self, history_file: str = ".agent_history", project_dir: str = None):
        self.history_file = Path.home() / history_file
        self.project_dir = project_dir
        self.session = PromptSession(
            history=FileHistory(str(self.history_file)),
            completer=CommandCompleter(project_dir=project_dir),
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
