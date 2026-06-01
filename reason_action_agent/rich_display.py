"""Rich 美化显示模块"""

import re
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.text import Text
from rich.theme import Theme
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from reason_action_agent.themes import get_theme, THEMES


class RichDisplay:
    """Rich 显示管理器"""
    
    def __init__(self, theme_name: str = "default"):
        self._theme_name = theme_name
        self.console = Console(theme=get_theme(theme_name))
        self._current_progress = None
    
    def set_theme(self, theme_name: str):
        """切换主题"""
        if theme_name not in THEMES:
            self.warning(f"主题 '{theme_name}' 不存在")
            return False
        
        self._theme_name = theme_name
        self.console = Console(theme=get_theme(theme_name))
        self.success(f"已切换到主题: {theme_name}")
        return True
    
    def get_theme(self) -> str:
        """获取当前主题名"""
        return self._theme_name
    
    def print(self, *args, **kwargs):
        """代理 console.print"""
        self.console.print(*args, **kwargs)
    
    def clear(self):
        """清屏"""
        self.console.clear()
    
    # ========== 基础组件（延迟导入） ==========
    
    def panel(self, title: str, content: str, style: str = "blue", expand: bool = False):
        """面板显示"""
        from rich.panel import Panel
        self.console.print(Panel(content, title=title, border_style=style, expand=expand))
    
    def markdown(self, content: str):
        """Markdown 渲染"""
        from rich.markdown import Markdown
        self.console.print(Markdown(content))
    
    def code(self, code: str, language: str = "python", line_numbers: bool = True, theme: str = "monokai"):
        """代码高亮"""
        from rich.syntax import Syntax
        self.console.print(Syntax(code, language, line_numbers=line_numbers, theme=theme))
    
    def table(self, title: str = None):
        """创建表格"""
        from rich.table import Table
        return Table(title=title, show_header=True, header_style="bold cyan")
    
    # ========== ReAct 专用显示 ==========
    
    def thought(self, content: str):
        """显示思考"""
        from rich.panel import Panel
        self.console.print(Panel(content, title="💭 思考", border_style="cyan"))
        self.console.print()
    
    def action(self, tool_name: str, args: list, kwargs: dict):
        """显示动作"""
        from rich.panel import Panel
        from rich.syntax import Syntax
        
        # 格式化参数
        params = []
        for arg in args:
            params.append(f"    {repr(arg)},")
        for key, value in kwargs.items():
            params.append(f"    {key}={repr(value)},")
        
        if params:
            code = f"{tool_name}(\n" + "\n".join(params) + "\n)"
        else:
            code = f"{tool_name}()"
        
        self.console.print(Panel(
            Syntax(code, "python", line_numbers=False, theme="monokai"),
            title="🔧 执行",
            border_style="yellow",
        ))
        self.console.print()
    
    def observation(self, content: str, max_lines: int = 50):
        """显示观察结果 - 智能渲染"""
        from rich.panel import Panel
        
        # 智能识别内容类型
        rendered = self._smart_render(content, max_lines)
        
        self.console.print(Panel(rendered, title="📋 观察结果", border_style="green"))
        self.console.print()
    
    def _smart_render(self, content: str, max_lines: int = 50) -> Text:
        """智能渲染内容"""
        lines = content.split("\n")
        
        # 1. 识别文件内容（带行号的格式）
        if self._is_file_content(content):
            return self._render_file_content(content, max_lines)
        
        # 2. 识别目录列表
        if self._is_directory_list(content):
            return self._render_directory_tree(content)
        
        # 3. 识别搜索结果
        if self._is_search_result(content):
            return self._render_search_result(content, max_lines)
        
        # 4. 识别表格数据
        if self._is_table_data(content):
            return self._render_table_data(content)
        
        # 5. 默认文本（截断）
        if len(lines) > max_lines:
            displayed = "\n".join(lines[:max_lines])
            hint = f"\n\n[dim]... 省略 {len(lines) - max_lines} 行（共 {len(lines)} 行）[/dim]"
            content = displayed + hint
        
        return Text(content)
    
    def _is_file_content(self, content: str) -> bool:
        """识别是否为文件内容（带行号格式）"""
        # 格式: 文件: /path/to/file (共 N 行)
        # ──────────────────────────────────────────────
        #      1│内容
        return bool(re.match(r'^文件:', content)) or bool(re.match(r'^\s*\d+│', content.split('\n')[2] if len(content.split('\n')) > 2 else ''))
    
    def _render_file_content(self, content: str, max_lines: int) -> Text:
        """渲染文件内容"""
        lines = content.split("\n")
        
        # 提取文件路径
        file_path = ""
        if lines[0].startswith("文件:"):
            file_path = lines[0].replace("文件:", "").strip().split("(")[0].strip()
        
        # 提取代码内容
        code_lines = []
        for line in lines:
            match = re.match(r'^\s*(\d+)│(.*)$', line)
            if match:
                code_lines.append(match.group(2))
        
        code_content = "\n".join(code_lines[:max_lines])
        
        # 检测语言
        language = self._detect_language(file_path) if file_path else None
        
        if language:
            # 返回 Syntax 对象（需要在 panel 外处理）
            return Text(code_content)
        else:
            return Text(content[:2000])  # 截断
    
    def _is_directory_list(self, content: str) -> bool:
        """识别是否为目录列表"""
        return content.startswith("📁") or "├──" in content or "└──" in content
    
    def _render_directory_tree(self, content: str) -> Text:
        """渲染目录树"""
        # 保持原有格式，但添加颜色
        lines = content.split("\n")
        colored_lines = []
        
        for line in lines:
            if "📁" in line:
                colored_lines.append(f"[directory]{line}[/directory]")
            elif "📄" in line:
                colored_lines.append(f"[file]{line}[/file]")
            else:
                colored_lines.append(line)
        
        return Text.from_markup("\n".join(colored_lines))
    
    def _is_search_result(self, content: str) -> bool:
        """识别是否为搜索结果"""
        # 格式: 文件名:行号:内容
        return bool(re.match(r'^[^:]+:\d+:', content.split('\n')[0] if content else ''))
    
    def _render_search_result(self, content: str, max_lines: int) -> Text:
        """渲染搜索结果"""
        lines = content.split("\n")[:max_lines]
        colored_lines = []
        
        for line in lines:
            # 格式: 文件名:行号:内容
            match = re.match(r'^([^:]+):(\d+):(.*)$', line)
            if match:
                file, line_num, text = match.groups()
                colored_lines.append(
                    f"[file_path]{file}[/file_path]:[line_number]{line_num}[/line_number]:{text}"
                )
            else:
                colored_lines.append(line)
        
        return Text.from_markup("\n".join(colored_lines))
    
    def _is_table_data(self, content: str) -> bool:
        """识别是否为表格数据"""
        lines = content.split("\n")
        # 简单判断：包含分隔线
        return len(lines) > 2 and any("─" in line or "|" in line for line in lines[:3])
    
    def _render_table_data(self, content: str) -> Text:
        """渲染表格数据"""
        return Text(content)  # 保持原样
    
    def _detect_language(self, file_path: str) -> Optional[str]:
        """检测文件语言"""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sh": "bash",
            ".bash": "bash",
            ".zsh": "zsh",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".xml": "xml",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".sql": "sql",
            ".md": "markdown",
            ".toml": "toml",
            ".ini": "ini",
        }
        
        ext = Path(file_path).suffix.lower()
        return ext_map.get(ext)
    
    def final_answer(self, content: str):
        """显示最终答案"""
        from rich.panel import Panel
        from rich.markdown import Markdown
        
        # 尝试 Markdown 渲染
        self.console.print(Panel(Markdown(content), title="✅ 最终答案", border_style="magenta"))
        self.console.print()
    
    def error(self, message: str, details: str = None):
        """显示错误"""
        from rich.panel import Panel
        
        content = f"[error]{message}[/error]"
        if details:
            content += f"\n\n[dim]{details}[/dim]"
        
        self.console.print(Panel(content, title="❌ 错误", border_style="red"))
        self.console.print()
    
    def warning(self, message: str):
        """显示警告"""
        from rich.panel import Panel
        self.console.print(Panel(message, title="⚠️  警告", border_style="yellow"))
        self.console.print()
    
    def info(self, message: str):
        """显示信息"""
        self.console.print(f"[info]ℹ️  {message}[/info]")
    
    def success(self, message: str):
        """显示成功"""
        self.console.print(f"[green]✓ {message}[/green]")
    
    # ========== 特殊场景 ==========
    
    def file_content(
        self,
        file_path: str,
        content: str,
        language: str = None,
        start_line: int = 1,
        total_lines: int = None,
    ):
        """显示文件内容"""
        from rich.syntax import Syntax
        
        header = f"[file_path]{file_path}[/file_path]"
        if total_lines:
            header += f" (第 {start_line}-{start_line + content.count(chr(10))} 行，共 {total_lines} 行)"
        
        self.console.print(header)
        self.console.print("─" * 60)
        
        if language:
            # 代码高亮
            self.console.print(Syntax(
                content,
                language,
                line_numbers=True,
                theme="monokai",
                start_line=start_line,
            ))
        else:
            # 普通文本，添加行号
            lines = content.split("\n")
            for i, line in enumerate(lines, start=start_line):
                self.console.print(f"[line_number]{i:6d}│[/line_number]{line}")
        
        self.console.print()
    
    def directory_tree(self, path: str, tree_str: str):
        """显示目录树"""
        from rich.panel import Panel
        self.console.print(Panel(tree_str, title=f"📁 {path}", border_style="blue"))
        self.console.print()
    
    def tool_list(self, tools: list):
        """显示工具列表"""
        from rich.table import Table
        
        table = Table(title="🔧 可用工具", show_header=True, header_style="bold cyan")
        table.add_column("工具名", style="cyan")
        table.add_column("签名", style="yellow")
        table.add_column("说明")
        
        for tool in tools:
            table.add_row(
                tool.name,
                tool.signature,
                tool.description.split("\n")[0] if tool.description else "",
            )
        
        self.console.print(table)
        self.console.print()
    
    def stats(self, stats: dict):
        """显示统计信息"""
        from rich.table import Table
        
        table = Table(title="📊 执行统计", show_header=True, header_style="bold cyan")
        table.add_column("指标", style="cyan")
        table.add_column("值", style="yellow")
        
        for key, value in stats.items():
            table.add_row(key, str(value))
        
        self.console.print(table)
        self.console.print()
    
    # ========== 启动画面 ==========
    
    def welcome(self, project_dir: str, model: str, protocol: str):
        """显示欢迎信息"""
        from rich.panel import Panel
        
        self.console.print()
        self.console.print(Panel(
            f"[bold cyan]🤖 ReAct Agent[/bold cyan]\n\n"
            f"[dim]一个学习型 AI Agent - 从零手写，深入理解每一行代码[/dim]\n\n"
            f"📂 工作目录: [blue]{project_dir}[/blue]\n"
            f"🧠 模型: [yellow]{model}[/yellow] ({protocol})\n"
            f"💬 输入任务开始对话，输入 [red]quit[/red] 退出",
            border_style="blue",
            expand=False,
        ))
        self.console.print()
    
    def goodbye(self):
        """显示告别信息"""
        self.console.print()
        self.console.print("[dim]👋 再见！期待下次相遇~[/dim]")
        self.console.print()
    
    # ========== 进度提示 ==========
    
    def thinking(self):
        """显示思考中"""
        self.console.print("[dim]🤔 思考中...[/dim]")
    
    def loading(self, message: str = "加载中"):
        """显示加载中"""
        self.console.print(f"[dim]⏳ {message}...[/dim]")
    
    def create_progress(self, description: str = "处理中"):
        """创建进度条"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
        )
    
    def start_progress(self, description: str = "处理中", total: int = 100):
        """开始进度"""
        if self._current_progress is None:
            self._current_progress = self.create_progress()
            self._current_progress.start()
        task_id = self._current_progress.add_task(description, total=total)
        return task_id
    
    def update_progress(self, task_id, advance: int = 1):
        """更新进度"""
        if self._current_progress:
            self._current_progress.update(task_id, advance=advance)
    
    def stop_progress(self):
        """停止进度"""
        if self._current_progress:
            self._current_progress.stop()
            self._current_progress = None


# 全局实例
display = RichDisplay()
