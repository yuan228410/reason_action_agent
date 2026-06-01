## 版本历史

### v1.6 (2026-04-22)
- 新增通讯录搜索能力（搜人/搜群），整合 address-search skill 能力
- 新增 `address_search.py` 脚本，复用公共 `auth.py` 和 `api_config.py` 模块
- `api_config.py` 新增 `address_search` 端点
- 搜索能力从 5 种扩展至 6 种
- 增加重要命令格式约束

### v1.5 (2026-04-10)
- 认证：`auth.py` 仅从本地 ugate token 缓存文件读取；缺失时退出码 2，由 Agent 调用 `get-ugate-token` skill（不再子进程调用 `ugate-auth`）

### v1.4 (2026-03-30)
- 优化会议搜索触发关键词，新增"上周的会议"、"关于XX的会议"等场景
- 明确会议搜索与 infoflow-calendar-meeting 的边界：
  - enterprise-search：搜索历史会议记录、跨人员查询会议
  - infoflow-calendar-meeting：查看个人会议日程、获取个人会议 ASR
- 完善触发优先级规则，区分"个人日程"与"历史会议搜索"场景
- 新增"我的会议"等个人性关键词优先使用 infoflow-calendar-meeting

### v1.3 (2026-03-30)
- 优化触发边界，新增触发优先级规则，解决与 fetch-weekly-content、infoflow-calendar-meeting 的触发冲突
- 明确"下属"、"团队"、"谁没交"、"未读周报"、"汇总"等管理性关键词优先使用 fetch-weekly-content
- 明确"日程"、"安排"、"今天/明天"、"本周"、"下周"等时间性关键词优先使用 infoflow-calendar-meeting

### v1.2 (2026-03-29)
- 认证模块重构：委托 ugate-auth skill 获取 token，与 ku-doc-manage 对齐方案
- 移除直接读取 token 缓存文件和过时的 fallback 路径
- 支持 exit code 2（用户授权）信号透传
- auth.py 新增 `get_fetch_headers()`，消除 3 个 fetch 脚本中手动转换 header 大小写的重复代码
- 移除未被引用的 config.yaml

### v1.1 (2026-03-26)
- 新增 MUST 触发条件，明确触发边界
- 新增 HARD-GATE 约束，限制 LLM 自我发挥
- 新增 3 个典型工作流图
- 抽取公共模块：auth.py、api_config.py、time_utils.py
- 消除约 560 行重复代码
- 统一时间参数处理，支持相对时间

### v1.0
- 初始版本，提供 5 种搜索能力和 3 种详情获取能力