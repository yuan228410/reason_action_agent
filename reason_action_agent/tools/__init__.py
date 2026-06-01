"""工具模块"""

from reason_action_agent.tools.registry import (
    ToolRegistry,
    tool,
    get_registry,
)
from reason_action_agent.tools.file_tools import (
    read_file,
    write_to_file,
    run_terminal_command,
    list_dir,
    edit_file,
    delete_file,
    search_files,
    rename_file,
    copy_file,
)
from reason_action_agent.tools.web_tools import (
    web_search,
    get_weather,
    fetch_url,
)
from reason_action_agent.tools.system_tools import (
    current_time,
    get_env,
    set_env,
    list_env,
    get_system_info,
)

__all__ = [
    # 注册器
    "ToolRegistry",
    "tool",
    "get_registry",
    # 文件工具
    "read_file",
    "write_to_file",
    "run_terminal_command",
    "list_dir",
    "edit_file",
    "delete_file",
    "search_files",
    "rename_file",
    "copy_file",
    # 网络工具
    "web_search",
    "get_weather",
    "fetch_url",
    # 系统工具
    "current_time",
    "get_env",
    "set_env",
    "list_env",
    "get_system_info",
]


def get_default_tools():
    """获取默认工具列表"""
    from reason_action_agent.tools.file_tools import (
        read_file,
        write_to_file,
        run_terminal_command,
        list_dir,
        edit_file,
        delete_file,
        search_files,
        rename_file,
        copy_file,
    )
    from reason_action_agent.tools.web_tools import (
        web_search,
        get_weather,
        fetch_url,
    )
    from reason_action_agent.tools.system_tools import (
        current_time,
        get_env,
        set_env,
        list_env,
        get_system_info,
    )
    from reason_action_agent.tools.skill_tools import (
        load_skill,
        list_skills,
        run_skill_script,
        read_skill_reference,
        get_skill_info,
    )
    
    return [
        # 文件操作
        read_file,
        write_to_file,
        run_terminal_command,
        list_dir,
        edit_file,
        delete_file,
        search_files,
        rename_file,
        copy_file,
        # 网络工具
        web_search,
        get_weather,
        fetch_url,
        # 系统工具
        current_time,
        get_env,
        set_env,
        list_env,
        get_system_info,
        # 技能工具
        load_skill,
        list_skills,
        run_skill_script,
        read_skill_reference,
        get_skill_info,
    ]
