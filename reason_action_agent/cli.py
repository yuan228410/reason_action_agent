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
    skills = agent.skill_manager.list_skills()
    if skills:
        display.info(f"已加载 {len(skills)} 个技能")
    display.info("输入 /help 查看命令，支持 Tab 自动补全")
    display.print()
    
    # 交互循环
    ctrl_c_count = 0  # Ctrl+C 计数器
    
    while True:
        try:
            # 使用增强输入管理器
            user_input = input_manager.get_input()
            
            # 处理 Ctrl+C
            if user_input == "__CTRL_C__":
                ctrl_c_count += 1
                if ctrl_c_count >= 2:
                    # 第二次 Ctrl+C，退出
                    display.goodbye()
                    break
                else:
                    # 第一次 Ctrl+C，提示
                    display.print()
                    display.warning("再按一次 Ctrl+C 退出，或输入任务继续")
                    continue
            
            # 用户输入了内容，重置计数器
            if user_input and user_input != "__CTRL_C__":
                ctrl_c_count = 0
            
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
            try:
                result = agent.run(user_input)
            except Exception as e:
                # 任务执行出错，友好提示
                display.error(f"任务执行失败: {e}")
                display.info("可以尝试重新描述任务或换一个任务")
                # 记录错误日志
                if config.log.enabled:
                    import traceback
                    display.print("[dim]详细错误已记录到日志[/dim]")
                continue
            
        except KeyboardInterrupt:
            # 执行任务时按 Ctrl+C
            display.print()
            display.warning("已取消当前操作")
            continue
        except Exception as e:
            # 捕获所有未预期的错误
            display.error(f"发生未知错误: {e}")
            display.info("程序将继续运行，可以尝试其他操作")
            if config.log.enabled:
                import traceback
                traceback.print_exc()
            continue


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
    
    # 清空历史
    if cmd == "/clear":
        agent.messages = None
        agent.exporter.clear()
        display.clear()
        display.success("已清空对话历史")
        return False
    
    # 清屏
    if cmd == "/cls":
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
    
    # 技能列表
    if cmd == "/skills":
        list_all_skills(agent)
        return False
    
    # 技能操作
    if cmd == "/skill":
        handle_skill_command(args, agent)
        return False
    
    # 未知命令
    display.warning(f"未知命令: {cmd}")
    display.info("输入 /help 查看可用命令")
    return False


def handle_skill_command(args: str, agent: ReActAgent):
    """处理技能命令"""
    parts = args.split(maxsplit=1)
    action = parts[0] if parts else ""
    params = parts[1] if len(parts) > 1 else ""
    
    manager = agent.skill_manager
    
    if action == "install":
        # /skill install <url|path> [--global|--project]
        level = "project" if "--project" in params else "global"
        params = params.replace("--global", "").replace("--project", "").strip()
        
        try:
            if params.startswith("http"):
                skill = manager.install_from_url(params, level)
            else:
                skill = manager.install_from_file(params, level)
            
            display.success(f"已安装技能: {skill.name} v{skill.metadata.version}")
            display.print(f"  描述: {skill.description}")
            display.print(f"  级别: {skill.level}")
            if skill.directory:
                display.print(f"  目录: {skill.directory}")
        except Exception as e:
            display.error(f"安装失败: {e}")
    
    elif action == "uninstall":
        # /skill uninstall <name>
        if manager.uninstall(params):
            display.success(f"已卸载技能: {params}")
        else:
            display.error(f"未找到技能: {params}")
    
    elif action == "load":
        # /skill load <name>
        content = manager.load_skill(params)
        if content:
            display.success(f"已加载技能: {params}")
        else:
            display.error(f"未找到技能: {params}")
    
    elif action == "info":
        # /skill info <name>
        info = manager.get_skill_info(params)
        if info:
            display.print(Panel(info, title=f"📖 {params}", border_style="blue"))
        else:
            display.error(f"未找到技能: {params}")
    
    elif action == "create":
        # /skill create <name> [--global|--project]
        level = "project" if "--project" in params else "global"
        name = params.replace("--global", "").replace("--project", "").strip()
        
        try:
            path = manager.create_skill_template(name, level)
            display.success(f"已创建技能模板: {name}")
            display.print(f"  目录: {path}")
            display.print(f"  请编辑 SKILL.md 添加技能内容")
        except Exception as e:
            display.error(str(e))
    
    elif action == "run":
        # /skill run <name> <script.py> [args...]
        parts = params.split(maxsplit=2)
        if len(parts) < 2:
            display.error("用法: /skill run <skill-name> <script.py> [args...]")
            return
        
        skill_name = parts[0]
        script_name = parts[1]
        args_list = parts[2].split() if len(parts) > 2 else []
        
        display.info(f"执行技能脚本: {skill_name}/{script_name}")
        result = manager.run_skill_script(skill_name, script_name, args_list)
        display.print(result)
    
    elif action == "read":
        # /skill read <name> <ref.md>
        parts = params.split(maxsplit=1)
        if len(parts) < 2:
            display.error("用法: /skill read <skill-name> <ref.md>")
            return
        
        skill_name = parts[0]
        ref_name = parts[1]
        
        result = manager.read_skill_reference(skill_name, ref_name)
        display.print(result)
    
    else:
        show_skill_help()


def list_all_skills(agent: ReActAgent):
    """列出所有技能"""
    skills = agent.skill_manager.list_skills()
    
    if not skills:
        display.info("暂无已安装的技能")
        display.print()
        display.print("使用以下命令安装:")
        display.print("  /skill install <url|path>")
        display.print()
        return
    
    from rich.table import Table
    
    table = Table(title="📚 可用技能", show_header=True, header_style="bold cyan")
    table.add_column("名称", style="cyan")
    table.add_column("版本", style="yellow")
    table.add_column("描述", style="white")
    table.add_column("级别", style="magenta")
    table.add_column("状态", style="green")
    
    for skill in skills:
        status = "✓ 已加载" if skill.loaded else "未加载"
        version = f"v{skill.metadata.version}" if skill.metadata.version else ""
        
        table.add_row(
            skill.name,
            version,
            skill.description[:40] + ("..." if len(skill.description) > 40 else ""),
            skill.level,
            status,
        )
    
    display.print(table)
    display.print()
    display.info("使用 load_skill(\"name\") 或 /skill load <name> 加载技能")


def show_skill_help():
    """显示技能帮助"""
    display.print(Panel(
        """
[bold]技能管理命令:[/bold]

  [cyan]/skills[/cyan]                     列出所有技能
  [cyan]/skill install <url|path>[/cyan]    安装技能
  [cyan]/skill uninstall <name>[/cyan]      卸载技能
  [cyan]/skill load <name>[/cyan]           加载技能
  [cyan]/skill info <name>[/cyan]           查看技能详情
  [cyan]/skill create <name>[/cyan]         创建技能模板
  [cyan]/skill run <name> <script>[/cyan]   执行技能脚本
  [cyan]/skill read <name> <ref>[/cyan]     读取参考文档

[bold]安装选项:[/bold]

  --global     安装到全局（默认）
  --project    安装到项目

[bold]使用示例:[/bold]

  [yellow]安装技能[/yellow]
  /skill install https://.../skill.md
  /skill install /path/to/skill-dir --project

  [yellow]查看技能[/yellow]
  /skill info enterprise-search

  [yellow]加载技能[/yellow]
  /skill load python-expert
  或让模型自动调用: load_skill("python-expert")

  [yellow]执行脚本[/yellow]
  /skill run enterprise-search neisou_search.py --word "关键词"

  [yellow]读取参考[/yellow]
  /skill read enterprise-search api_docs.md

  [yellow]创建技能[/yellow]
  /skill create my-workflow --project
        """,
        title="📖 技能帮助",
        border_style="blue",
    ))


def show_help():
    """显示帮助"""
    display.print(Panel(
        """
[bold]斜杠命令:[/bold]

  [cyan]/help[/cyan]            显示此帮助
  [cyan]/tools[/cyan]           查看工具列表
  [cyan]/skills[/cyan]          查看技能列表
  [cyan]/themes[/cyan]          查看主题列表
  [cyan]/theme <name>[/cyan]    切换主题（Tab 补全）
  [cyan]/export <fmt>[/cyan]    导出会话（md/html，Tab 补全）
  [cyan]/stats[/cyan]           查看执行统计
  [cyan]/clear[/cyan]           清空对话历史并清屏
  [cyan]/cls[/cyan]             仅清屏
  [cyan]/quit, /q[/cyan]        退出程序

[bold]使用示例:[/bold]

  [yellow]查看文件[/yellow]    读取 README.md 文件
  [yellow]搜索代码[/yellow]    搜索包含 "def " 的 Python 文件
  [yellow]运行命令[/yellow]    执行 pip list 查看已安装包
  [yellow]问答[/yellow]        什么是 ReAct 模式？

[bold]提示:[/bold]

  • 输入 [cyan]/[/cyan] 后按 [bold]Tab[/bold] 自动补全命令
  • 命令参数也支持 Tab 补全（主题名、导出格式）
  • 对话历史会自动保留，直到使用 [cyan]/clear[/cyan] 清空
  • 文件路径建议使用绝对路径
  • 终端命令执行前会要求确认
  • 使用 [cyan]/skill[/cyan] 管理技能
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
