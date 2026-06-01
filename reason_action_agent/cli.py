"""CLI 入口"""

import click

from reason_action_agent.agent import ReActAgent
from reason_action_agent.config import load_config
from reason_action_agent.session_logger import SessionLogger


@click.command()
@click.argument("project_directory", type=click.Path(exists=True), default=".")
@click.option("--model", "-m", help="模型名称")
@click.option("--protocol", "-p", type=click.Choice(["openai", "anthropic"]), help="协议类型")
@click.option("--log-dir", "-l", default="logs", help="日志目录")
@click.option("--no-log", is_flag=True, help="禁用日志")
def main(project_directory: str, model: str | None, protocol: str | None, log_dir: str, no_log: bool):
    """ReAct Agent - AI 编程助手
    
    PROJECT_DIRECTORY: 工作目录，默认为当前目录
    """
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
    
    # 初始化 Agent
    agent = ReActAgent(config=config)
    
    print(f"🤖 ReAct Agent 已启动")
    print(f"📂 工作目录: {project_directory}")
    print(f"🧠 模型: {config.model.name} ({config.model.protocol})")
    print(f"📝 日志: {'启用' if config.log.enabled else '禁用'}")
    print("-" * 50)
    
    # 交互循环
    while True:
        try:
            user_input = input("\n💬 请输入任务（输入 'quit' 退出）: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n👋 再见！")
                break
            
            result = agent.run(user_input)
            print(f"\n\n✅ Final Answer: {result}")
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n\n❌ 错误: {e}")


if __name__ == "__main__":
    main()
