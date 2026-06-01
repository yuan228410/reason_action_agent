"""CLI 入口"""

import click

from reason_action_agent.agent import ReActAgent
from reason_action_agent.config import load_config
from reason_action_agent.rich_display import display
from reason_action_agent.themes import list_themes, get_theme_info
from reason_action_agent.input_manager import InputManager
from reason_action_agent.session_logger import SessionLogger
from rich.panel import Panel


@click.command()
@click.argument("project_directory", type=click.Path(exists=True), default=".")
@click.option("--model", "-m", help="模型名称")
@click.option("--protocol", "-p", type=click.Choice(["openai", "anthropic"]), help="协议类型")
@click.option("--log-dir", "-l", default="logs", help="日志目录")
@click.option("--no-log", is_flag=True, help="禁用日志")
@click.option("--no-clear", is_flag=True, help="不清屏")
@click.option("--theme", "-t", default="default", help="颜色主题")
def main(project_directory: str, model: str | None, protocol: str | None, log_dir: str, no_log: bool, no_clear: bool, theme: str):
    """ReAct Agent - AI 编程助手
    
    PROJECT_DIRECTORY: 工作目录，默认为当前目录
    """
    # 清屏
    if not no_clear:
        display.clear()
    
    # 设置主题
    display.set_theme(theme)
    
    # 加载配置
    config = load_config()
    config.project_directory = project_directory
    
    # 覆盖配置
    if model:
        config.model.name = model
    if protocol:
        config.model.protocol = protocol
    if no_log:
        config.log.enabled = False
    else:
        config.log.dir = log_dir
    
    # 初始化
    agent = ReActAgent(config=config)
    input_manager = InputManager()
    
    # 显示欢迎信息
    display.welcome(
        project_dir=project_directory,
        model=config.model.name,
        protocol=config.model.protocol,
    )
    
    # 显示可用工具
    display.info(f"已加载 {len(agent.registry.list_tools())} 个工具")
    display.info("输入 /help 查看命令，支持 Tab 自动补全")
    display.print()
    
    # 交互循环
    while True:
        try:
            # 使用增强输入管理器
            user_input = input_manager.get_input()
            
            if not user_input:
                continue
            
            # 处理斜杠命令
            if input_manager.is_command(user_input):
                cmd, args = input_manager.parse_command(user_input)
                should_exit = handle_slash_command(cmd, args, agent)
                if should_exit:
                    break
                continue
            
            # 检查是否输入了旧命令（不带 /）
            old_commands = ["help", "tools", "themes", "clear", "quit", "exit", "q", "stats", "export"]
            if user_input.lower() in old_commands or user_input.lower().startswith("theme "):
                display.info(f"提示：命令需要以 / 开头，如 /{user_input.lower()}")
                continue
            
            # 执行任务
            result = agent.run(user_input)
            
        except KeyboardInterrupt:
            display.print()
            display.warning("已取消当前操作")
            continue
        except Exception as e:
            display.error(str(e), details=type(e).__name__)
            import traceback
            if config.log.enabled:
                display.print("[dim]详细错误已记录到日志[/dim]")


def handle_slash_command(cmd: str, args: str, agent: ReActAgent) -> bool:
    """处理斜杠命令，返回是否退出"""
    
    # 退出
    if cmd in ["/quit", "/q"]:
        display.goodbye()
        return True
    
    # 帮助
    if cmd == "/help":
        show_help()
        return False
    
    # 工具列表
    if cmd == "/tools":
        display.tool_list(agent.registry.list_tools())
        return False
    
    # 清屏
    if cmd == "/clear":
        display.clear()
        return False
    
    # 主题列表
    if cmd == "/themes":
        display.print(get_theme_info())
        return False
    
    # 切换主题
    if cmd == "/theme":
        if not args:
            display.warning("请指定主题名，如: /theme monokai")
            display.print(get_theme_info())
        else:
            display.set_theme(args)
        return False
    
    # 导出
    if cmd == "/export":
        if not args:
            show_export_help()
        elif args == "md":
            filepath = agent.exporter.export_markdown()
            display.success(f"已导出为 Markdown: {filepath}")
        elif args == "html":
            filepath = agent.exporter.export_html()
            display.success(f"已导出为 HTML: {filepath}")
        else:
            display.warning(f"不支持的导出格式: {args}")
        return False
    
    # 统计
    if cmd == "/stats":
        display.stats(agent.exporter.get_stats())
        return False
    
    # 未知命令
    display.warning(f"未知命令: {cmd}")
    display.info("输入 /help 查看可用命令")
    return False


def show_help():
    """显示帮助"""
    display.print(Panel(
        """
[bold]斜杠命令:[/bold]

  [cyan]/help[/cyan]            显示此帮助
  [cyan]/tools[/cyan]           查看工具列表
  [cyan]/themes[/cyan]          查看主题列表
  [cyan]/theme <name>[/cyan]    切换主题（Tab 补全）
  [cyan]/export <fmt>[/cyan]    导出会话（md/html，Tab 补全）
  [cyan]/stats[/cyan]           查看执行统计
  [cyan]/clear[/cyan]           清屏
  [cyan]/quit, /q[/cyan]        退出程序

[bold]使用示例:[/bold]

  [yellow]查看文件[/yellow]    读取 README.md 文件
  [yellow]搜索代码[/yellow]    搜索包含 "def " 的 Python 文件
  [yellow]运行命令[/yellow]    执行 pip list 查看已安装包
  [yellow]问答[/yellow]        什么是 ReAct 模式？

[bold]提示:[/bold]

  • 输入 [cyan]/[/cyan] 后按 [bold]Tab[/bold] 自动补全命令
  • 命令参数也支持 Tab 补全（主题名、导出格式）
  • 文件路径建议使用绝对路径
  • 终端命令执行前会要求确认
        """,
        title="📖 帮助",
        border_style="blue",
    ))
    display.print()


def show_export_help():
    """显示导出帮助"""
    display.print(Panel(
        """
[bold]导出命令:[/bold]

  [cyan]/export md[/cyan]       导出为 Markdown 文件
  [cyan]/export html[/cyan]     导出为 HTML 文件（带样式）

导出文件保存在: [blue]exports/session_YYYYMMDD_HHMMSS.[ext][/blue]

[bold]说明:[/bold]

  • Markdown: 适合版本控制、笔记整理
  • HTML: 适合分享、演示（带丰富样式）
  • 自动记录所有步骤：思考、执行、观察、答案

[bold]使用示例:[/bold]

  输入 [cyan]/export md[/cyan] 导出 Markdown
  输入 [cyan]/export html[/cyan] 导出 HTML
        """,
        title="📤 导出会话",
        border_style="green",
    ))
    display.print()


if __name__ == "__main__":
    main()
