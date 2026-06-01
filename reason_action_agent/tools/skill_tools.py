"""技能工具 - 支持按需加载和脚本执行"""

from reason_action_agent.tools.registry import tool
from typing import Optional, List

# 全局管理器
_skill_manager = None


def init_skill_manager(project_dir: str = None):
    """初始化技能管理器"""
    global _skill_manager
    from reason_action_agent.skill_manager import SkillManager
    _skill_manager = SkillManager(project_dir)


def get_skill_manager():
    """获取技能管理器"""
    global _skill_manager
    if _skill_manager is None:
        from reason_action_agent.skill_manager import SkillManager
        _skill_manager = SkillManager()
    return _skill_manager


@tool
def load_skill(skill_name: str) -> str:
    """
    加载技能的完整内容（按需加载）
    
    使用场景：
    - 需要使用某个技能时加载其完整内容
    - 根据任务需求加载特定技能
    
    参数说明：
    - skill_name: 技能名称
    
    返回：技能的完整内容（包含脚本和参考文档信息）
    
    示例：
    - load_skill("python-expert")
    - load_skill("enterprise-search")
    """
    manager = get_skill_manager()
    content = manager.load_skill(skill_name)
    
    if content:
        skill = manager.get_skill(skill_name)
        result = f"✓ 已加载技能 [{skill_name}]\n\n{content}"
        
        # 提示可用的工具
        if skill and (skill.scripts_dir or skill.references_dir):
            result += "\n\n---\n\n**可用工具**:\n"
            if skill.scripts_dir:
                result += f"- `run_skill_script(\"{skill_name}\", \"script.py\")` - 执行脚本\n"
            if skill.references_dir:
                result += f"- `read_skill_reference(\"{skill_name}\", \"ref.md\")` - 查看参考文档\n"
        
        return result
    else:
        return f"❌ 未找到技能: {skill_name}。使用 list_skills() 查看可用技能。"


@tool
def list_skills() -> str:
    """
    列出所有可用技能
    
    使用场景：
    - 查看当前有哪些技能可用
    - 了解技能的描述和版本
    
    返回：技能列表（包含名称、版本、描述、状态）
    
    示例：
    - list_skills()
    """
    manager = get_skill_manager()
    skills = manager.list_skills()
    
    if not skills:
        return "暂无可用技能。使用 /skill install 安装技能。"
    
    lines = ["📚 可用技能:\n"]
    for skill in skills:
        status = "✓ 已加载" if skill.loaded else "未加载"
        version = f"v{skill.metadata.version}" if skill.metadata.version else ""
        namespace = f"({skill.metadata.namespace}) " if skill.metadata.namespace else ""
        
        lines.append(f"**{skill.name}** {namespace}{version}: {skill.description} [{status}]")
        lines.append(f"  加载: `load_skill(\"{skill.name}\")`\n")
    
    return "\n".join(lines)


@tool
def run_skill_script(skill_name: str, script_name: str, args: List[str] = None) -> str:
    """
    执行技能脚本
    
    使用场景：
    - 执行技能提供的脚本
    - 调用技能的自动化工具
    
    参数说明：
    - skill_name: 技能名称
    - script_name: 脚本文件名（如 "search.py"）
    - args: 脚本参数列表（可选）
    
    返回：脚本执行结果
    
    示例：
    - run_skill_script("enterprise-search", "neisou_search.py", ["--word", "关键词"])
    - run_skill_script("data-analyst", "generate_report.py")
    """
    manager = get_skill_manager()
    
    # 确保技能已加载
    if skill_name not in manager.get_loaded_skills():
        manager.load_skill(skill_name)
    
    result = manager.run_skill_script(skill_name, script_name, args)
    return result


@tool
def read_skill_reference(skill_name: str, ref_name: str) -> str:
    """
    读取技能参考文档
    
    使用场景：
    - 查看技能的参考文档
    - 了解技能的详细使用说明
    
    参数说明：
    - skill_name: 技能名称
    - ref_name: 参考文档文件名（如 "api_docs.md"）
    
    返回：参考文档内容
    
    示例：
    - read_skill_reference("enterprise-search", "api_docs.md")
    - read_skill_reference("data-analyst", "visualization_guide.md")
    """
    manager = get_skill_manager()
    
    # 确保技能已加载
    if skill_name not in manager.get_loaded_skills():
        manager.load_skill(skill_name)
    
    result = manager.read_skill_reference(skill_name, ref_name)
    return result


@tool
def get_skill_info(skill_name: str) -> str:
    """
    获取技能详细信息
    
    使用场景：
    - 查看技能的详细元数据
    - 了解技能的目录结构和资源
    
    参数说明：
    - skill_name: 技能名称
    
    返回：技能详细信息（版本、作者、目录等）
    
    示例：
    - get_skill_info("python-expert")
    """
    manager = get_skill_manager()
    info = manager.get_skill_info(skill_name)
    
    if info:
        return info
    else:
        return f"❌ 未找到技能: {skill_name}"
