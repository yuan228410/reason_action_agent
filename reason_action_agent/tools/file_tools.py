"""文件操作工具"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from reason_action_agent.tools.registry import tool


@tool
def read_file(
    file_path: str,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
    encoding: Optional[str] = None,
    max_chars: Optional[int] = 10000,
) -> str:
    """
    读取文件内容，支持行号范围和编码检测
    
    使用场景：
    - 查看完整文件：read_file("/path/to/file")
    - 分段读取：read_file("/path/to/file", start_line=1, end_line=50)
    - 指定编码：read_file("/path/to/file", encoding="gbk")
    - 读取大文件：read_file("/path/to/file", max_chars=None)  # 不限制输出
    
    参数说明：
    - file_path: 文件绝对路径（必须）
    - start_line: 起始行号（从1开始），不传则从第1行开始
    - end_line: 结束行号（含），不传则读到末尾
    - encoding: 文件编码，不传则自动检测
    - max_chars: 最大输出字符数（默认 10000），设为 None 则不限制
    
    返回：带行号的文件内容
    
    示例：
    - read_file("/tmp/test.py")
    - read_file(file_path="/tmp/test.py", start_line=10, end_line=20)
    - read_file(file_path="/tmp/large.py", max_chars=None)  # 读取完整内容
    """
    path = Path(file_path)
    
    if not path.exists():
        return f"错误：文件不存在 {file_path}"
    
    if not path.is_file():
        return f"错误：不是文件 {file_path}"
    
    # 检查文件大小（性能优化：大文件预警）
    file_size = path.stat().st_size
    if file_size > 10_000_000:  # 10MB
        return f"⚠️  文件过大 ({file_size / 1_000_000:.1f}MB)，建议使用分段读取或 search_files 搜索内容"
    
    # 检测编码
    if encoding is None:
        encoding = _detect_encoding(file_path)
    
    try:
        # 性能优化：如果指定了行号范围，只读取需要的行
        if start_line is not None or end_line is not None:
            lines = []
            with open(file_path, "r", encoding=encoding) as f:
                start = (start_line or 1) - 1
                end = end_line or float('inf')
                
                for i, line in enumerate(f):
                    if i >= start and i < end:
                        lines.append(line)
                    elif i >= end:
                        break
            
            total_lines = _count_lines_fast(file_path) if end_line is None else end
            selected_count = len(lines)
        else:
            # 读取全部内容
            with open(file_path, "r", encoding=encoding) as f:
                lines = f.readlines()
            total_lines = len(lines)
            selected_count = total_lines
        
        # 处理行号范围
        start = (start_line or 1) - 1  # 转为 0-based
        end = end_line or total_lines
        
        # 边界检查
        start = max(0, start)
        end = min(total_lines, end)
        
        if start >= total_lines:
            return f"错误：起始行号 {start_line} 超出文件范围（共 {total_lines} 行）"
        
        # 添加行号（性能优化：使用生成器）
        result_lines = (f"{i:6d}│{line}" for i, line in enumerate(lines, start=start + 1))
        result = "".join(result_lines)
        
        # 添加提示信息
        if start_line or end_line:
            result = f"文件: {file_path} (第 {start+1}-{end} 行，共 {total_lines} 行)\n{'─'*60}\n{result}"
        else:
            result = f"文件: {file_path} (共 {total_lines} 行)\n{'─'*60}\n{result}"
        
        # 限制输出长度（如果设置了 max_chars）
        if max_chars is not None and len(result) > max_chars:
            # 截断并给出引导提示
            truncated = result[:max_chars]
            
            hint = f"""

⚠️  输出已截断（共 {len(result):,} 字符，仅显示前 {max_chars:,} 字符）

💡 建议使用以下方式获取完整内容：
- 读取完整文件：read_file(file_path="{file_path}", max_chars=None)
- 分段读取：read_file(file_path="{file_path}", start_line=1, end_line=50)
- 搜索特定内容：search_files(pattern="关键词", directory="{Path(file_path).parent}")
- 使用 grep 命令：run_terminal_command("grep '关键词' {file_path}")"""
            
            result = truncated + hint
        
        return result
    
    except UnicodeDecodeError:
        return f"错误：无法用 {encoding} 编码读取文件，请尝试指定 encoding 参数"
    except Exception as e:
        return f"读取文件失败: {e}"


@tool
def write_to_file(
    file_path: str,
    content: str,
    mode: str = "overwrite",
    create_dirs: bool = True,
) -> str:
    """
    将内容写入文件，支持追加模式和自动创建目录
    
    使用场景：
    - 覆盖写入：write_to_file("/path/to/file", "内容")
    - 追加内容：write_to_file("/path/to/file", "新内容", mode="append")
    - 多行内容：write_to_file("/path/to/file", "第一行\\n第二行\\n第三行")
    
    参数说明：
    - file_path: 文件绝对路径（必须）
    - content: 要写入的内容（必须），多行用 \\n 分隔
    - mode: 写入模式
        - "overwrite": 覆盖文件（默认）
        - "append": 追加到末尾
    - create_dirs: 是否自动创建父目录（默认 True）
    
    返回：操作结果
    
    示例：
    - write_to_file("/tmp/test.txt", "Hello World")
    - write_to_file(file_path="/tmp/test.txt", content="Line 1\\nLine 2", mode="append")
    """
    path = Path(file_path)
    
    # 创建父目录
    if create_dirs and not path.parent.exists():
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return f"创建目录失败: {e}"
    
    # 检查模式
    if mode not in ["overwrite", "append"]:
        return f"错误：不支持的写入模式 '{mode}'，请使用 'overwrite' 或 'append'"
    
    try:
        write_mode = "a" if mode == "append" else "w"
        with open(file_path, write_mode, encoding="utf-8") as f:
            f.write(content.replace("\\n", "\n"))
        
        action = "追加到" if mode == "append" else "写入"
        return f"✓ 成功{action}文件: {file_path}"
    
    except Exception as e:
        return f"写入文件失败: {e}"


@tool
def run_terminal_command(
    command: str,
    cwd: Optional[str] = None,
    timeout: int = 30,
    max_output: Optional[int] = 10000,
) -> str:
    """
    执行终端命令（危险操作需谨慎）
    
    使用场景：
    - 安装依赖：run_terminal_command("pip install requests")
    - 运行脚本：run_terminal_command("python main.py", cwd="/path/to/project")
    - 系统命令：run_terminal_command("ls -la")
    - 获取完整输出：run_terminal_command("ls -la /usr/bin", max_output=None)
    
    参数说明：
    - command: 要执行的命令（必须）
    - cwd: 工作目录（不传则使用当前目录）
    - timeout: 超时秒数（默认 30）
    - max_output: 最大输出字符数（默认 10000），设为 None 则不限制
    
    返回：命令输出或错误信息
    
    示例：
    - run_terminal_command("ls -la")
    - run_terminal_command(command="python test.py", cwd="/tmp/project", timeout=60)
    - run_terminal_command(command="cat large_file.txt", max_output=None)  # 不限制输出
    
    注意：危险命令（rm -rf、格式化等）执行前会在 <thought> 中说明目的
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
        )
        
        # 组合 stdout 和 stderr
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"
        
        # 限制输出长度（如果设置了 max_output）
        if max_output is not None and len(output) > max_output:
            truncated = output[:max_output]
            
            hint = f"""

⚠️  输出已截断（共 {len(output):,} 字符，仅显示前 {max_output:,} 字符）

💡 建议使用以下方式获取完整输出：
- 获取完整输出：run_terminal_command(command="{command}", max_output=None)
- 重定向到文件：{command} > output.txt
- 使用分页：{command} | less
- 筛选关键内容：{command} | grep "关键词"
- 增加输出限制：run_terminal_command(command="{command}", max_output=50000)"""
            
            output = truncated + hint
        
        if result.returncode != 0:
            return f"命令执行失败 (退出码: {result.returncode})\n{output}"
        
        return output or "✓ 执行成功（无输出）"
    
    except subprocess.TimeoutExpired:
        return f"错误：命令执行超时（{timeout} 秒）"
    except Exception as e:
        return f"执行命令失败: {e}"


@tool
def list_dir(
    directory: str = ".",
    recursive: bool = False,
    max_depth: int = 3,
    include: Optional[str] = None,
) -> str:
    """
    列出目录内容（树形结构显示）
    
    使用场景：
    - 查看项目结构：list_dir(recursive=True)
    - 只看某类文件：list_dir(include="*.py")
    - 指定目录：list_dir("/path/to/project", recursive=True)
    
    参数说明：
    - directory: 目录路径（默认当前目录）
    - recursive: 是否递归列出子目录（默认 False）
    - max_depth: 递归最大深度（默认 3）
    - include: 文件名过滤（glob 模式），如 "*.py", "*.md"
    
    返回：树形目录结构
    
    示例：
    - list_dir()
    - list_dir(directory="/tmp/project", recursive=True, include="*.py")
    """
    path = Path(directory)
    
    if not path.exists():
        return f"错误：目录不存在 {directory}"
    
    if not path.is_dir():
        return f"错误：不是目录 {directory}"
    
    lines = []
    lines.append(f"📁 {path.absolute()}")
    lines.append("─" * 60)
    
    def _list_dir(p: Path, depth: int = 0, prefix: str = ""):
        if depth > max_depth:
            return
        
        try:
            items = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        except PermissionError:
            lines.append(f"{prefix}└── [无权限访问]")
            return
        
        # 过滤文件
        if include:
            items = [
                item for item in items
                if item.is_dir() or Path(item.name).match(include)
            ]
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            
            if item.is_dir():
                lines.append(f"{prefix}{current_prefix}📁 {item.name}/")
                if recursive:
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    _list_dir(item, depth + 1, next_prefix)
            else:
                size = _format_file_size(item.stat().st_size)
                lines.append(f"{prefix}{current_prefix}📄 {item.name} ({size})")
    
    _list_dir(path)
    
    result = "\n".join(lines)
    
    # 限制输出长度
    max_chars = 10000
    if len(result) > max_chars:
        truncated = result[:max_chars]
        
        hint = f"""

⚠️  输出已截断（共 {len(result):,} 字符）

💡 建议使用以下方式获取完整列表：
- 查看特定目录：list_dir(directory="子目录路径", recursive=False)
- 过滤文件类型：list_dir(directory="{directory}", include="*.py")
- 非递归查看：list_dir(directory="{directory}", recursive=False)
- 减少深度：list_dir(directory="{directory}", max_depth=2)"""
        
        result = truncated + hint
    
    return result


@tool
def edit_file(
    file_path: str,
    old_string: str,
    new_string: str,
    replace_all: bool = False,
) -> str:
    """
    编辑文件：查找并替换内容（推荐用于精确修改）
    
    使用场景：
    - 修改配置：edit_file("/path/to/config.py", "DEBUG=False", "DEBUG=True")
    - 批量替换：edit_file("/path/to/file", "old", "new", replace_all=True)
    
    参数说明：
    - file_path: 文件绝对路径（必须）
    - old_string: 要查找的原始字符串（必须，精确匹配）
    - new_string: 替换为的新字符串（必须）
    - replace_all: 是否替换所有匹配（默认 False，只替换第一个）
    
    返回：替换结果（成功数量或错误信息）
    
    示例：
    - edit_file("/tmp/config.py", "VERSION = '1.0'", "VERSION = '2.0'")
    - edit_file(file_path="/tmp/test.py", old_string="foo", new_string="bar", replace_all=True)
    """
    path = Path(file_path)
    
    if not path.exists():
        return f"错误：文件不存在 {file_path}"
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 查找匹配
        count = content.count(old_string)
        if count == 0:
            return f"错误：未找到匹配内容"
        
        # 替换
        if replace_all:
            new_content = content.replace(old_string, new_string)
            replaced = count
        else:
            new_content = content.replace(old_string, new_string, 1)
            replaced = 1
        
        # 写回文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        return f"✓ 成功替换 {replaced} 处匹配"
    
    except Exception as e:
        return f"编辑文件失败: {e}"


@tool
def delete_file(
    file_path: str,
    recursive: bool = False,
    missing_ok: bool = False,
) -> str:
    """
    删除文件或目录
    
    Args:
        file_path: 文件或目录路径
        recursive: 是否递归删除目录及其内容，默认 False
        missing_ok: 路径不存在时是否静默忽略，默认 False
    
    Returns:
        操作结果
    """
    path = Path(file_path)
    
    if not path.exists():
        if missing_ok:
            return f"✓ 文件不存在，已忽略: {file_path}"
        return f"错误：文件不存在 {file_path}"
    
    try:
        if path.is_file():
            path.unlink()
            return f"✓ 已删除文件: {file_path}"
        elif path.is_dir():
            if recursive:
                shutil.rmtree(path)
                return f"✓ 已删除目录及其内容: {file_path}"
            else:
                try:
                    path.rmdir()  # 只能删除空目录
                    return f"✓ 已删除空目录: {file_path}"
                except OSError:
                    return f"错误：目录非空，需要设置 recursive=True"
        else:
            return f"错误：未知文件类型 {file_path}"
    
    except Exception as e:
        return f"删除失败: {e}"


@tool
def search_files(
    pattern: str,
    directory: str = ".",
    include: Optional[str] = None,
    max_results: int = 50,
    max_chars: Optional[int] = 10000,
) -> str:
    """
    搜索文件内容（类似 grep，支持正则表达式）
    
    使用场景：
    - 搜索代码：search_files("def ", include="*.py")
    - 查找 TODO：search_files("# TODO", directory="/path/to/project")
    - 正则匹配：search_files(r"import \\w+", include="*.py")
    - 获取所有结果：search_files("TODO", max_results=None, max_chars=None)
    
    参数说明：
    - pattern: 搜索模式（支持正则表达式，必须）
    - directory: 搜索目录（默认当前目录）
    - include: 文件名过滤（glob 模式），如 "*.py", "*.md"
    - max_results: 最大返回结果数（默认 50），设为 None 则不限制
    - max_chars: 最大输出字符数（默认 10000），设为 None 则不限制
    
    返回：匹配结果列表（文件:行号: 内容）
    
    示例：
    - search_files("TODO", include="*.py")
    - search_files(pattern="def main", directory="/tmp/project", include="*.py")
    - search_files(pattern="import", max_results=None, max_chars=None)  # 获取所有结果
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        return f"错误：目录不存在 {directory}"
    
    results = []
    regex = re.compile(pattern)
    
    try:
        # 遍历文件
        for file_path in dir_path.rglob("*"):
            if not file_path.is_file():
                continue
            
            # 文件名过滤
            if include and not file_path.match(include):
                continue
            
            # 跳过大文件和二进制文件
            try:
                if file_path.stat().st_size > 1_000_000:  # 1MB
                    continue
            except:
                continue
            
            # 搜索内容
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        if regex.search(line):
                            results.append(f"{file_path}:{line_num}: {line.rstrip()}")
                            # 如果设置了 max_results，检查是否达到限制
                            if max_results is not None and len(results) >= max_results:
                                break
            except:
                continue
            
            # 如果设置了 max_results，检查是否达到限制
            if max_results is not None and len(results) >= max_results:
                break
        
        if not results:
            return f"未找到匹配 '{pattern}' 的内容"
        
        output = "\n".join(results)
        
        # 限制输出长度（如果设置了 max_chars）
        if max_chars is not None and len(output) > max_chars:
            truncated = output[:max_chars]
            total_matches = len(results)
            
            hint = f"""

⚠️  输出已截断（共 {total_matches} 个匹配，仅显示前 {max_chars:,} 字符）

💡 建议使用以下方式优化搜索：
- 获取完整结果：search_files(pattern="{pattern}", max_results=None, max_chars=None)
- 缩小搜索范围：search_files(pattern="{pattern}", directory="具体目录")
- 过滤文件类型：search_files(pattern="{pattern}", include="*.py")
- 更精确的模式：search_files(pattern="更精确的正则表达式", include="*.py")
- 减少结果数量：search_files(pattern="{pattern}", max_results=10)"""
            
            output = truncated + hint
        
        return output
    
    except Exception as e:
        return f"搜索失败: {e}"


@tool
def rename_file(
    src_path: str,
    dst_path: str,
    overwrite: bool = False,
) -> str:
    """
    重命名或移动文件/目录
    
    Args:
        src_path: 原路径
        dst_path: 目标路径
        overwrite: 目标已存在时是否覆盖，默认 False
    
    Returns:
        操作结果
    """
    src = Path(src_path)
    dst = Path(dst_path)
    
    if not src.exists():
        return f"错误：源路径不存在 {src_path}"
    
    if dst.exists() and not overwrite:
        return f"错误：目标已存在 {dst_path}，需要设置 overwrite=True"
    
    try:
        # 创建目标父目录
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        # 移动/重命名
        shutil.move(str(src), str(dst))
        return f"✓ 已移动: {src_path} → {dst_path}"
    
    except Exception as e:
        return f"移动失败: {e}"


@tool
def copy_file(
    src_path: str,
    dst_path: str,
    overwrite: bool = False,
) -> str:
    """
    复制文件或目录
    
    Args:
        src_path: 源路径
        dst_path: 目标路径
        overwrite: 目标已存在时是否覆盖，默认 False
    
    Returns:
        操作结果
    """
    src = Path(src_path)
    dst = Path(dst_path)
    
    if not src.exists():
        return f"错误：源路径不存在 {src_path}"
    
    if dst.exists() and not overwrite:
        return f"错误：目标已存在 {dst_path}，需要设置 overwrite=True"
    
    try:
        # 创建目标父目录
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        # 复制
        if src.is_file():
            shutil.copy2(src, dst)
        else:
            shutil.copytree(src, dst, dirs_exist_ok=overwrite)
        
        return f"✓ 已复制: {src_path} → {dst_path}"
    
    except Exception as e:
        return f"复制失败: {e}"


# ============ 辅助函数 ============

def _detect_encoding(file_path: str) -> str:
    """检测文件编码"""
    # 简单实现：尝试常见编码
    encodings = ["utf-8", "gbk", "gb2312", "utf-16", "latin1"]
    
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                f.read(1024)  # 尝试读取一小段
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    return "utf-8"  # 默认


def _format_file_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def _count_lines_fast(file_path: str) -> int:
    """快速统计文件行数（不加载全部内容）"""
    try:
        with open(file_path, "rb") as f:
            count = 0
            for _ in f:
                count += 1
        return count
    except:
        return 0
