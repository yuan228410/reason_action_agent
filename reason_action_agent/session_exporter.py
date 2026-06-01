"""会话导出模块 - 支持导出为 Markdown/HTML"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, field


@dataclass
class SessionStep:
    """会话步骤"""
    type: str  # thought, action, observation, final_answer
    content: str
    tool_name: str = ""
    args: list = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


class SessionExporter:
    """会话导出器"""
    
    def __init__(self, project_dir: str = ""):
        self.project_dir = project_dir
        self.steps: List[SessionStep] = []
        self.start_time = datetime.now()
        self.user_input = ""
    
    def add_user_input(self, content: str):
        """添加用户输入"""
        self.user_input = content
        self.steps.append(SessionStep(type="user_input", content=content))
    
    def add_thought(self, content: str):
        """添加思考"""
        self.steps.append(SessionStep(type="thought", content=content))
    
    def add_action(self, tool_name: str, args: list, kwargs: dict):
        """添加动作"""
        self.steps.append(SessionStep(
            type="action",
            content=self._format_tool_call(tool_name, args, kwargs),
            tool_name=tool_name,
            args=args,
            kwargs=kwargs,
        ))
    
    def add_observation(self, content: str):
        """添加观察"""
        self.steps.append(SessionStep(type="observation", content=content))
    
    def add_final_answer(self, content: str):
        """添加最终答案"""
        self.steps.append(SessionStep(type="final_answer", content=content))
    
    def add_error(self, content: str):
        """添加错误"""
        self.steps.append(SessionStep(type="error", content=content))
    
    def _format_tool_call(self, tool_name: str, args: list, kwargs: dict) -> str:
        """格式化工具调用"""
        params = [repr(arg) for arg in args]
        params.extend(f"{k}={repr(v)}" for k, v in kwargs.items())
        return f"{tool_name}({', '.join(params)})"
    
    def clear(self):
        """清空会话"""
        self.steps = []
        self.user_input = ""
        self.start_time = datetime.now()
    
    def export_markdown(self, filepath: str = None) -> str:
        """导出为 Markdown"""
        if filepath is None:
            filepath = self._generate_filepath("md")
        
        lines = []
        
        # 标题
        lines.append(f"# ReAct Agent 会话记录")
        lines.append(f"")
        lines.append(f"**时间**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**项目**: {self.project_dir}")
        lines.append(f"**任务**: {self.user_input}")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
        
        # 步骤
        step_num = 0
        for step in self.steps:
            if step.type == "user_input":
                lines.append(f"## 📝 用户任务")
                lines.append(f"")
                lines.append(f"{step.content}")
                lines.append(f"")
            
            elif step.type == "thought":
                step_num += 1
                lines.append(f"### 💭 步骤 {step_num}: 思考")
                lines.append(f"")
                lines.append(f"{step.content}")
                lines.append(f"")
            
            elif step.type == "action":
                lines.append(f"**🔧 执行工具**: `{step.content}`")
                lines.append(f"")
            
            elif step.type == "observation":
                lines.append(f"**📋 观察结果**:")
                lines.append(f"")
                lines.append(f"```")
                # 截断过长的观察结果
                content = step.content
                if len(content) > 2000:
                    content = content[:2000] + "\n... (已截断)"
                lines.append(content)
                lines.append(f"```")
                lines.append(f"")
            
            elif step.type == "final_answer":
                lines.append(f"---")
                lines.append(f"")
                lines.append(f"## ✅ 最终答案")
                lines.append(f"")
                lines.append(f"{step.content}")
                lines.append(f"")
            
            elif step.type == "error":
                lines.append(f"**❌ 错误**: {step.content}")
                lines.append(f"")
        
        # 统计
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"**统计**:")
        lines.append(f"- 总步骤数: {step_num}")
        lines.append(f"- 持续时间: {(datetime.now() - self.start_time).seconds} 秒")
        lines.append(f"")
        lines.append(f"> 由 ReAct Agent 生成 @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 写入文件
        content = "\n".join(lines)
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        Path(filepath).write_text(content, encoding="utf-8")
        
        return filepath
    
    def export_html(self, filepath: str = None) -> str:
        """导出为 HTML"""
        if filepath is None:
            filepath = self._generate_filepath("html")
        
        html_parts = []
        
        # HTML 头部
        html_parts.append(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ReAct Agent 会话记录</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }}
        .header h1 {{ margin-bottom: 10px; }}
        .meta {{ opacity: 0.9; font-size: 14px; }}
        .content {{ padding: 30px; }}
        .step {{
            margin-bottom: 25px;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #ddd;
        }}
        .step-title {{
            font-weight: 600;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .thought {{ border-color: #0ea5e9; background: #f0f9ff; }}
        .thought .step-title {{ color: #0ea5e9; }}
        .action {{ border-color: #f59e0b; background: #fffbeb; }}
        .action .step-title {{ color: #f59e0b; }}
        .observation {{ border-color: #10b981; background: #f0fdf4; }}
        .observation .step-title {{ color: #10b981; }}
        .final-answer {{
            border-color: #8b5cf6;
            background: linear-gradient(135deg, #f5f3ff 0%, #faf5ff 100%);
            border-width: 4px;
        }}
        .final-answer .step-title {{ color: #8b5cf6; font-size: 18px; }}
        .final-answer .step-content {{ font-size: 16px; }}
        .error {{ border-color: #ef4444; background: #fef2f2; }}
        .error .step-title {{ color: #ef4444; }}
        .step-content {{
            font-size: 14px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        code {{
            background: #f1f5f9;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: "Monaco", "Menlo", monospace;
            font-size: 13px;
        }}
        pre {{
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            font-family: "Monaco", "Menlo", monospace;
            font-size: 13px;
            line-height: 1.5;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #999;
            font-size: 12px;
            border-top: 1px solid #eee;
        }}
        .emoji {{ font-size: 18px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="emoji">🤖</span> ReAct Agent 会话记录</h1>
            <div class="meta">
                <div>时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}</div>
                <div>项目: {self.project_dir}</div>
                <div>任务: {self.user_input}</div>
            </div>
        </div>
        <div class="content">
""")
        
        # 步骤
        step_num = 0
        for step in self.steps:
            if step.type == "user_input":
                html_parts.append(f"""            <div class="step">
                <div class="step-title"><span class="emoji">📝</span> 用户任务</div>
                <div class="step-content">{self._escape_html(step.content)}</div>
            </div>
""")
            
            elif step.type == "thought":
                step_num += 1
                html_parts.append(f"""            <div class="step thought">
                <div class="step-title"><span class="emoji">💭</span> 步骤 {step_num}: 思考</div>
                <div class="step-content">{self._escape_html(step.content)}</div>
            </div>
""")
            
            elif step.type == "action":
                html_parts.append(f"""            <div class="step action">
                <div class="step-title"><span class="emoji">🔧</span> 执行工具</div>
                <div class="step-content"><code>{self._escape_html(step.content)}</code></div>
            </div>
""")
            
            elif step.type == "observation":
                content = step.content
                if len(content) > 2000:
                    content = content[:2000] + "\n... (已截断)"
                html_parts.append(f"""            <div class="step observation">
                <div class="step-title"><span class="emoji">📋</span> 观察结果</div>
                <div class="step-content"><pre>{self._escape_html(content)}</pre></div>
            </div>
""")
            
            elif step.type == "final_answer":
                html_parts.append(f"""            <div class="step final-answer">
                <div class="step-title"><span class="emoji">✅</span> 最终答案</div>
                <div class="step-content">{self._markdown_to_html(step.content)}</div>
            </div>
""")
            
            elif step.type == "error":
                html_parts.append(f"""            <div class="step error">
                <div class="step-title"><span class="emoji">❌</span> 错误</div>
                <div class="step-content">{self._escape_html(step.content)}</div>
            </div>
""")
        
        # HTML 尾部
        html_parts.append(f"""        </div>
        <div class="footer">
            统计: {step_num} 个步骤 | 持续时间: {(datetime.now() - self.start_time).seconds} 秒<br>
            由 ReAct Agent 生成 @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>""")
        
        # 写入文件
        content = "\n".join(html_parts)
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        Path(filepath).write_text(content, encoding="utf-8")
        
        return filepath
    
    def _generate_filepath(self, ext: str) -> str:
        """生成文件路径"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_{timestamp}.{ext}"
        return os.path.join(self.project_dir, "exports", filename)
    
    def _escape_html(self, text: str) -> str:
        """转义 HTML"""
        return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))
    
    def _markdown_to_html(self, text: str) -> str:
        """简单 Markdown 转 HTML"""
        # 标题
        text = text.replace("\n### ", "\n<h4>").replace("\n## ", "\n<h3>").replace("\n# ", "\n<h2>")
        # 粗体
        text = text.replace("**", "<strong>").replace("**", "</strong>")
        # 代码
        text = text.replace("`", "<code>").replace("`", "</code>")
        # 换行
        text = text.replace("\n", "<br>")
        return text
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        thought_count = sum(1 for s in self.steps if s.type == "thought")
        action_count = sum(1 for s in self.steps if s.type == "action")
        duration = (datetime.now() - self.start_time).seconds
        
        return {
            "思考次数": thought_count,
            "工具调用": action_count,
            "总步骤": len(self.steps),
            "持续时间": f"{duration} 秒",
        }
