"""技能管理器 - 完整支持标准 Skills"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import yaml
import re
import json
import shutil


@dataclass
class SkillMetadata:
    """技能元数据（标准字段）"""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "unknown"
    tags: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # 扩展字段（从 .skill-meta.json）
    namespace: Optional[str] = None
    skill_id: Optional[int] = None
    full_name: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SkillMetadata':
        """从字典创建"""
        return cls(
            name=data.get('name', 'unknown'),
            description=data.get('description', ''),
            version=data.get('version', '1.0.0'),
            author=data.get('author', 'unknown'),
            tags=data.get('tags', []),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            namespace=data.get('namespace'),
            skill_id=data.get('skill_id'),
            full_name=data.get('full_name'),
        )


@dataclass
class Skill:
    """技能定义"""
    metadata: SkillMetadata
    content: str  # Markdown 正文
    path: Path  # SKILL.md 路径
    level: str  # global, project
    loaded: bool = False
    
    # 目录相关
    directory: Optional[Path] = None  # 技能目录
    scripts_dir: Optional[Path] = None  # 脚本目录
    references_dir: Optional[Path] = None  # 参考文档目录
    assets_dir: Optional[Path] = None  # 资源目录
    
    @property
    def name(self) -> str:
        return self.metadata.name
    
    @property
    def description(self) -> str:
        return self.metadata.description
    
    def get_script_path(self, script_name: str) -> Optional[Path]:
        """获取脚本路径"""
        if self.scripts_dir:
            script_path = self.scripts_dir / script_name
            if script_path.exists():
                return script_path
        return None
    
    def get_reference_path(self, ref_name: str) -> Optional[Path]:
        """获取参考文档路径"""
        if self.references_dir:
            ref_path = self.references_dir / ref_name
            if ref_path.exists():
                return ref_path
        return None


class SkillManager:
    """技能管理器"""
    
    GLOBAL_DIR = Path.home() / ".agent" / "skills"
    
    def __init__(self, project_dir: str = None):
        self.project_dir = Path(project_dir) if project_dir else None
        self._skills_cache: Dict[str, Skill] = {}
        self._loaded_skills: Dict[str, str] = {}
        self._ensure_dirs()
        self._load_skills_index()
    
    def _ensure_dirs(self):
        """确保目录存在"""
        self.GLOBAL_DIR.mkdir(parents=True, exist_ok=True)
        if self.project_dir:
            (self.project_dir / ".agent" / "skills").mkdir(parents=True, exist_ok=True)
    
    def _load_skills_index(self):
        """加载技能索引（支持目录和单文件结构）"""
        # 全局技能
        self._load_skills_from_dir(self.GLOBAL_DIR, "global")
        
        # 项目技能（优先级更高）
        if self.project_dir:
            project_skills = self.project_dir / ".agent" / "skills"
            if project_skills.exists():
                self._load_skills_from_dir(project_skills, "project")
    
    def _load_skills_from_dir(self, base_dir: Path, level: str):
        """从目录加载技能"""
        for path in base_dir.iterdir():
            if path.is_dir():
                # 目录结构：查找 SKILL.md
                skill_file = path / "SKILL.md"
                if skill_file.exists():
                    skill = self._parse_skill(skill_file, level, directory=path)
                    if skill:
                        # 加载 .skill-meta.json（如果存在）
                        meta_file = path / ".skill-meta.json"
                        if meta_file.exists():
                            self._load_skill_meta(skill, meta_file)
                        
                        self._skills_cache[skill.name] = skill
            elif path.is_file() and path.suffix == ".md":
                # 单文件结构
                skill = self._parse_skill(path, level)
                if skill:
                    self._skills_cache[skill.name] = skill
    
    def _parse_skill(self, path: Path, level: str, directory: Path = None) -> Optional[Skill]:
        """解析技能（支持 frontmatter）"""
        try:
            content = path.read_text(encoding="utf-8")
            
            # 解析 YAML frontmatter
            if content.startswith("---"):
                match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
                if match:
                    yaml_content = match.group(1)
                    body = match.group(2)
                    
                    # 解析 YAML
                    metadata_dict = yaml.safe_load(yaml_content)
                    metadata = SkillMetadata.from_dict(metadata_dict)
                    
                    # 创建技能对象
                    skill = Skill(
                        metadata=metadata,
                        content=body.strip(),
                        path=path,
                        level=level,
                        directory=directory,
                    )
                    
                    # 设置子目录
                    if directory:
                        skill.scripts_dir = directory / "scripts" if (directory / "scripts").exists() else None
                        skill.references_dir = directory / "references" if (directory / "references").exists() else None
                        skill.assets_dir = directory / "assets" if (directory / "assets").exists() else None
                    
                    return skill
            
            # 无 frontmatter，使用文件名
            return Skill(
                metadata=SkillMetadata(name=path.stem, description=""),
                content=content,
                path=path,
                level=level,
            )
        except Exception as e:
            print(f"解析技能失败 {path}: {e}")
            return None
    
    def _load_skill_meta(self, skill: Skill, meta_file: Path):
        """加载 .skill-meta.json 元数据"""
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            # 更新元数据
            if 'version' in meta:
                skill.metadata.version = meta['version']
            if 'namespace' in meta:
                skill.metadata.namespace = meta['namespace']
            if 'skill_id' in meta:
                skill.metadata.skill_id = meta['skill_id']
            if 'full_name' in meta:
                skill.metadata.full_name = meta['full_name']
        except Exception as e:
            print(f"加载元数据失败 {meta_file}: {e}")
    
    # ========== 核心方法 ==========
    
    def list_skills(self) -> List[Skill]:
        """列出所有技能（只返回元数据）"""
        return list(self._skills_cache.values())
    
    def get_skill_info(self, name: str) -> Optional[str]:
        """获取技能信息"""
        skill = self._skills_cache.get(name)
        if not skill:
            return None
        
        info = f"**{skill.metadata.name}**"
        if skill.metadata.namespace:
            info += f" ({skill.metadata.namespace})"
        info += f" v{skill.metadata.version}\n\n"
        info += f"{skill.metadata.description}\n\n"
        info += f"作者: {skill.metadata.author}\n"
        if skill.metadata.tags:
            info += f"标签: {', '.join(skill.metadata.tags)}\n"
        info += f"级别: {skill.level}\n"
        info += f"状态: {'✓ 已加载' if skill.loaded else '未加载'}\n"
        
        # 目录信息
        if skill.directory:
            info += f"目录: {skill.directory}\n"
        if skill.scripts_dir:
            info += f"脚本: {skill.scripts_dir}\n"
        if skill.references_dir:
            info += f"参考: {skill.references_dir}\n"
        
        return info
    
    def load_skill(self, name: str) -> Optional[str]:
        """加载技能完整内容"""
        # 已加载
        if name in self._loaded_skills:
            return self._loaded_skills[name]
        
        skill = self._skills_cache.get(name)
        if not skill:
            return None
        
        # 构建完整内容
        content = skill.content
        
        # 添加脚本信息
        if skill.scripts_dir:
            scripts = list(skill.scripts_dir.glob("*.py"))
            if scripts:
                content += "\n\n## 可用脚本\n\n"
                for script in scripts:
                    content += f"- `{script.name}`\n"
                content += f"\n使用 `run_skill_script(\"{name}\", \"script.py\")` 执行脚本\n"
        
        # 添加参考文档信息
        if skill.references_dir:
            refs = list(skill.references_dir.glob("*.md"))
            if refs:
                content += "\n\n## 参考文档\n\n"
                for ref in refs:
                    content += f"- `{ref.name}`\n"
                content += f"\n使用 `read_skill_reference(\"{name}\", \"ref.md\")` 查看文档\n"
        
        # 缓存
        self._loaded_skills[name] = content
        skill.loaded = True
        
        return content
    
    def get_loaded_skills(self) -> Dict[str, str]:
        """获取已加载的技能"""
        return self._loaded_skills.copy()
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """获取技能对象"""
        return self._skills_cache.get(name)
    
    # ========== 脚本和参考文档 ==========
    
    def run_skill_script(self, skill_name: str, script_name: str, args: List[str] = None) -> str:
        """执行技能脚本"""
        skill = self._skills_cache.get(skill_name)
        if not skill:
            return f"未找到技能: {skill_name}"
        
        script_path = skill.get_script_path(script_name)
        if not script_path:
            return f"未找到脚本: {script_name}"
        
        # 执行脚本
        import subprocess
        import os
        
        # 设置环境变量
        env = os.environ.copy()
        if skill.directory:
            env['SKILL_DIR'] = str(skill.directory)
        if skill.scripts_dir:
            env['SKILL_SCRIPTS_DIR'] = str(skill.scripts_dir)
        
        # 构建命令
        cmd = ['python3', str(script_path)]
        if args:
            cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(skill.directory) if skill.directory else None,
                env=env,
            )
            
            if result.returncode != 0:
                return f"脚本执行失败:\n{result.stderr}"
            
            return result.stdout
        except Exception as e:
            return f"执行失败: {e}"
    
    def read_skill_reference(self, skill_name: str, ref_name: str) -> str:
        """读取技能参考文档"""
        skill = self._skills_cache.get(skill_name)
        if not skill:
            return f"未找到技能: {skill_name}"
        
        ref_path = skill.get_reference_path(ref_name)
        if not ref_path:
            return f"未找到参考文档: {ref_name}"
        
        try:
            return ref_path.read_text(encoding="utf-8")
        except Exception as e:
            return f"读取失败: {e}"
    
    # ========== 安装/卸载 ==========
    
    def install_from_url(self, url: str, level: str = "global") -> Skill:
        """从 URL 安装"""
        import requests
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        content = response.text
        
        return self._install_content(content, level)
    
    def install_from_file(self, file_path: str, level: str = "global") -> Skill:
        """从本地文件安装"""
        path = Path(file_path)
        
        # 如果是目录，复制整个目录
        if path.is_dir():
            return self._install_directory(path, level)
        
        # 单文件
        content = path.read_text(encoding="utf-8")
        return self._install_content(content, level)
    
    def install_from_content(self, content: str, level: str = "global") -> Skill:
        """从内容安装"""
        return self._install_content(content, level)
    
    def _install_directory(self, source_dir: Path, level: str) -> Skill:
        """安装技能目录"""
        # 检查是否有 SKILL.md
        skill_file = source_dir / "SKILL.md"
        if not skill_file.exists():
            raise ValueError("技能目录必须包含 SKILL.md 文件")
        
        # 解析技能名称
        skill = self._parse_skill(skill_file, level, directory=source_dir)
        if not skill:
            raise ValueError("无法解析技能文件")
        
        # 添加创建时间
        if not skill.metadata.created_at:
            skill.metadata.created_at = datetime.now().isoformat()
        skill.metadata.updated_at = datetime.now().isoformat()
        
        # 复制目录
        target_dir = self._get_dir(level) / skill.name
        if target_dir.exists():
            shutil.rmtree(target_dir)
        
        shutil.copytree(source_dir, target_dir)
        
        # 更新缓存
        skill.path = target_dir / "SKILL.md"
        skill.directory = target_dir
        skill.scripts_dir = target_dir / "scripts" if (target_dir / "scripts").exists() else None
        skill.references_dir = target_dir / "references" if (target_dir / "references").exists() else None
        skill.assets_dir = target_dir / "assets" if (target_dir / "assets").exists() else None
        
        self._skills_cache[skill.name] = skill
        
        return skill
    
    def _install_content(self, content: str, level: str) -> Skill:
        """安装技能内容"""
        # 解析元数据
        skill = self._parse_skill_from_content(content, level)
        
        # 添加创建时间
        if not skill.metadata.created_at:
            skill.metadata.created_at = datetime.now().isoformat()
        skill.metadata.updated_at = datetime.now().isoformat()
        
        # 重新生成内容
        full_content = self._generate_skill_file(skill)
        
        # 保存文件
        target_dir = self._get_dir(level)
        target_path = target_dir / f"{skill.name}.md"
        target_path.write_text(full_content, encoding="utf-8")
        
        # 更新缓存
        skill.path = target_path
        self._skills_cache[skill.name] = skill
        
        return skill
    
    def uninstall(self, name: str) -> bool:
        """卸载技能"""
        skill = self._skills_cache.get(name)
        if not skill:
            return False
        
        # 删除文件或目录
        if skill.directory and skill.directory.exists():
            shutil.rmtree(skill.directory)
        elif skill.path.exists():
            skill.path.unlink()
        
        # 清理缓存
        del self._skills_cache[name]
        if name in self._loaded_skills:
            del self._loaded_skills[name]
        
        return True
    
    # ========== 工具方法 ==========
    
    def _parse_skill_from_content(self, content: str, level: str) -> Skill:
        """从内容解析技能"""
        if content.startswith("---"):
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
            if match:
                yaml_content = match.group(1)
                body = match.group(2)
                
                metadata_dict = yaml.safe_load(yaml_content)
                metadata = SkillMetadata.from_dict(metadata_dict)
                
                return Skill(
                    metadata=metadata,
                    content=body.strip(),
                    path=None,
                    level=level,
                )
        
        return Skill(
            metadata=SkillMetadata(name="unknown", description=""),
            content=content,
            path=None,
            level=level,
        )
    
    def _generate_skill_file(self, skill: Skill) -> str:
        """生成技能文件内容"""
        metadata_dict = {
            'name': skill.metadata.name,
            'description': skill.metadata.description,
            'version': skill.metadata.version,
            'author': skill.metadata.author,
            'tags': skill.metadata.tags,
            'created_at': skill.metadata.created_at,
            'updated_at': skill.metadata.updated_at,
        }
        
        yaml_content = yaml.dump(metadata_dict, allow_unicode=True, sort_keys=False)
        
        return f"---\n{yaml_content}---\n\n{skill.content}"
    
    def _get_dir(self, level: str) -> Path:
        """获取存储目录"""
        if level == "project" and self.project_dir:
            return self.project_dir / ".agent" / "skills"
        return self.GLOBAL_DIR
    
    def create_skill_template(self, name: str, level: str = "global") -> Path:
        """创建技能模板（目录结构）"""
        # 创建目录
        target_dir = self._get_dir(level) / name
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建 SKILL.md
        skill_file = target_dir / "SKILL.md"
        template = f"""---
name: {name}
description: 技能描述
version: 1.0.0
author: your-name
tags:
  - tag1
  - tag2
---

# {name}

技能说明...

## MUST 触发条件

以下场景必须使用本技能：

|| 触发关键词 | 典型示例 |
||-----------|---------|
|| 关键词1 | "示例1" |
|| 关键词2 | "示例2" |

## 核心能力

- 能力1
- 能力2

## 工作流程

1. 步骤1
2. 步骤2

## 示例

### 输入
示例输入

### 输出
示例输出
"""
        skill_file.write_text(template, encoding="utf-8")
        
        # 创建子目录
        (target_dir / "scripts").mkdir(exist_ok=True)
        (target_dir / "references").mkdir(exist_ok=True)
        
        # 创建 README
        readme = target_dir / "references" / "README.md"
        readme.write_text(f"# {name} 参考资料\n\n在这里添加参考文档...\n", encoding="utf-8")
        
        # 重新加载索引
        self._load_skills_index()
        
        return target_dir
