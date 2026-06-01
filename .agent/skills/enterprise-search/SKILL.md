---
name: enterprise-search
description: 百度企业内部六类关键词搜索（内搜/通讯录/会议/知识库/OKR/周报）。搜人搜群、找文档、检索任意人会议/周报/OKR 时使用。需深度分析OKR→用 fetch-okr-content；汇总下属周报→用 fetch-weekly-content。
---

# 企业搜索

## MUST 触发条件

**以下场景必须使用本 skill**：

| 触发关键词 | 典型示例 |
|-----------|---------|
| 内搜搜索 | "帮我内搜一下"、"搜一下内部文档"、"查找公司知识" |
| 会议搜索 | "搜索会议记录"、"找一下关于X的会议"、"查会议"、"上周的会议"、"关于XX的会议" |
| 周报搜索 | "搜索周报"、"找张三的周报"、"查看团队周报" |
| 知识库搜索 | "搜内部某个主题的知识库文档"、"找XX发给我的文档"、"找秋桐写的文档" |
| OKR搜索 | "搜索OKR"、"查张三的OKR"、"找Q1的OKR" |
| 搜人 | "找一下秋桐的联系方式"、"搜一下张三"、"查找某人邮箱/手机号/座位号"、"找XX的工号" |
| 搜群 | "搜一下XX群"、"找一下搜索相关的群"、"查群组" |

**不应触发本 skill 的场景**：
- 用户要查看**个人**会议日程/安排 → 使用 `infoflow-calendar-meeting` skill
- 用户要获取**个人**会议 ASR/会议纪要 → 使用 `infoflow-calendar-meeting` skill
- 用户要操作知识库文档（创建/移动） → 使用 `ku-doc-manage` skill
- 用户要查看/管理下属周报（如"谁没交周报"、"团队周报汇总"） → 使用 `fetch-weekly-content` skill
- **用户要查询团队/部门周报汇总（如"查看XX下面所有人的周报"、"XX部门周报汇总"） → 使用 `fetch-weekly-content` skill，禁止通过内搜搜索拼凑团队成员**

**触发优先级规则**（当存在歧义时）：
1. 提及"下属"、"团队"、"谁没交"、"未读周报"、"汇总"、"XX下面所有人"、"XX部门周报"等管理性关键词 → 优先使用 `fetch-weekly-content`
   - **禁止通过内搜搜索拼凑团队成员，必须使用 fetch-weekly-content 获取准确的下属关系**
2. 提及"**我的**会议"、"**我的**日程"、"今天/明天"、"本周"、"下周"等**个人**时间性关键词 → 优先使用 `infoflow-calendar-meeting`
3. **搜索历史会议记录**（如"搜索会议记录"、"找关于X的会议"、"上周的会议"、"关于XX的会议"）→ 使用本 skill `meeting_search.py`
4. **跨人员查询会议**（查询他人或特定人员的会议）→ 使用本 skill `meeting_search.py`
5. **非直属周报查询**（如"查同事的周报"、"部门内其他人的周报"、"关系不明的人员周报"）→ 使用本 skill `weekly_report_search.py`
   - 流向说明：若 `fetch-weekly-content` 返回 `error_code=NOT_SUBORDINATE`，自动转向此 skill 执行全量周报搜索
6. 其他场景 → 使用本 skill 进行搜索和详情获取

---

## HARD-GATE 约束

> **LLM 强制约束**：以下规则不可违反，请勿自行发挥或扩展。

### 1. 脚本调用约束

**只允许调用以下脚本，不得调用其他脚本或发明新参数**：

| 脚本 | 用途 | 必需参数 |
|-----|------|---------|
| `neisou_search.py` | 内搜搜索 | `--word` |
| `neisou_fetch.py` | 内搜详情获取 | `--resource-url` |
| `meeting_search.py` | 会议搜索 | `--q` |
| `weekly_report_search.py` | 周报搜索 | `--query` |
| `weekly_report_fetch.py` | 周报详情获取 | `--uuap`, `--date` |
| `ku_search.py` | 知识库搜索 | `--word` |
| `okr_search.py` | OKR搜索 | `--query` |
| `okr_fetch.py` | OKR详情获取 | `--uid` 或 `--uuap`, `--year` |
| `address_search.py` | 通讯录搜索（搜人/搜群） | `--type`, `--q` |

### 2. 时间参数约束

**时间参数格式支持**：
- 日期：`2026-03-16`
- 日期时间：`2026-03-16 09:00`
- 相对时间：`today`, `yesterday`, `last_week`, `this_week`, `last_month`
- 时间戳：会议搜索使用秒级，周报搜索使用毫秒级（脚本自动处理）

### 3. 详情获取前置约束

**禁止直接调用 fetch 脚本**，必须先通过搜索获取必要参数：
- `neisou_fetch.py` → 需要先 `neisou_search.py` 获取 `resource-url`
- `weekly_report_fetch.py` → 需要先 `weekly_report_search.py` 获取 `uuap`
- `okr_fetch.py` → 需要先 `okr_search.py` 获取 `uid`

### 4. resultType 路由约束

内搜搜索结果的 `resultType` 决定详情获取方式：
- `resultType=0/3` → 使用 `neisou_fetch.py`
- `resultType=16` → 知识库数据，使用 `ku-doc-manage` skill
- 其他类型 → 搜索摘要已足够，无需获取详情

---

## 典型工作流

### 工作流 1：搜索并获取详情

```
┌─────────────────────────────────────────────────────────────┐
│  搜索并获取详情（通用流程）                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 用户请求                                                 │
│     │                                                       │
│     ▼                                                       │
│  2. 判断搜索类型 ─────┬─ 内搜 → neisou_search.py            │
│     │                ├─ 会议 → meeting_search.py            │
│     │                ├─ 周报 → weekly_report_search.py      │
│     │                ├─ 知识库 → ku_search.py               │
│     │                ├─ OKR → okr_search.py                 │
│     │                └─ 搜人/搜群 → address_search.py       │
│     │                                                       │
│     ▼                                                       │
│  3. 分析搜索结果                                             │
│     │                                                       │
│     ├── 结果已满足需求 ──→ 直接输出给用户                     │
│     │                                                       │
│     └── 需要完整内容 ──→ 判断类型                            │
│                          │                                  │
│                          ├── 内搜 → 检查 resultType         │
│                          │         │                        │
│                          │         ├── 0/3 → neisou_fetch   │
│                          │         └── 16 → ku-doc-manage     │
│                          │                                  │
│                          ├── 周报 → weekly_report_fetch     │
│                          └── OKR → okr_fetch                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 工作流 2：知识库自然语言搜索

```
┌─────────────────────────────────────────────────────────────┐
│  知识库自然语言搜索                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  用户：找秋桐写过的文档                                       │
│     │                                                       │
│     ▼                                                       │
│  ku_search.py --word "找秋桐写过的文档" --click-nl-query     │
│     │                                                       │
│     ▼                                                       │
│  解读结果，向用户展示文档列表                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 工作流 3：团队周报分析

```
┌─────────────────────────────────────────────────────────────┐
│  团队周报分析                                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  用户：帮我整理张三、李四、王五上周周报的重点                   │
│     │                                                       │
│     ▼                                                       │
│  1. 搜索各人周报（可并行）                                    │
│     weekly_report_search.py --query "张三的周报"             │
│     weekly_report_search.py --query "李四的周报"             │
│     weekly_report_search.py --query "王五的周报"             │
│     │                                                       │
│     ▼                                                       │
│  2. 从结果提取 uuap，获取详情                                 │
│     weekly_report_fetch.py --uuap "zhangsan" --date "xxx"   │
│     weekly_report_fetch.py --uuap "lisi" --date "xxx"       │
│     weekly_report_fetch.py --uuap "wangwu" --date "xxx"     │
│     │                                                       │
│     ▼                                                       │
│  3. 分析处理：提炼重点、归纳总结、对比分析                     │
│     │                                                       │
│     ▼                                                       │
│  4. 输出精美格式 + HTML文件                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 能力速查表

### 搜索能力

| 搜索能力 | 搜索范围 | 命令行脚本 |
|---------|---------|-----------|
| 内搜搜索 | 百度内部知识文档、百科、Family论坛等资源 | `python3 scripts/neisou_search.py --word "关键词"` |
| 会议搜索 | 百度内部会议记录 | `python3 scripts/meeting_search.py --q "关键词"` |
| 周报搜索 | 百度内部周报 | `python3 scripts/weekly_report_search.py --query "关键词"` |
| 知识库搜索 | 知识库(ku.baidu-int.com)文档，支持自然语言语义搜索 | `python3 scripts/ku_search.py --word "关键词" [--click-nl-query]` |
| OKR搜索 | 百度内部OKR记录 | `python3 scripts/okr_search.py --query "关键词"` |
| 搜人 | 百度企业通讯录用户（按姓名、邮箱、手机号等） | `python3 scripts/address_search.py --type "corpuser" --q "关键词"` |
| 搜群 | 百度企业群组（按群名称、群成员等） | `python3 scripts/address_search.py --type "group" --q "关键词"` |

### 详情获取能力

| 获取能力 | 说明 | 命令行脚本 |
|---------|------|-----------|
| 内搜详情获取 | 根据资源URL获取内搜结果的完整内容（仅限resultType=0/3） | `python3 scripts/neisou_fetch.py --resource-url "https://..."` |
| 周报详情获取 | 根据uuap和日期获取指定周报的详细内容 | `python3 scripts/weekly_report_fetch.py --uuap "zhangsan" --date "2026-03-16"` |
| OKR详情获取 | 根据uuap/uid、年份和季度获取OKR详细内容 | `python3 scripts/okr_fetch.py --uid "1103145" --year 2026 --quarter "Q1"` |

---

## 详细参数说明

### 内搜搜索 (neisou_search.py)

**搜索范围**：百度内部知识文档、百科、课程等资源

| 参数 | 说明 |
|-----|------|
| --word | 搜索关键词（必需） |
| --page | 页码，默认 1 |

> **resultType 路由**：搜索结果包含 `resultType` 字段：
> - `0/3`：使用 `neisou_fetch.py` 获取完整内容
> - `16`：知识库数据，使用 `ku-doc-manage` skill
> - 其他：搜索摘要已足够

### 会议搜索 (meeting_search.py)

**搜索范围**：百度内部会议记录

| 参数 | 说明 |
|-----|------|
| --q | 检索词（必需，检索主题或参会人） |
| --page | 页码，默认 1 |
| --page-size | 每页数量，默认 20 |
| --start-time | 会议开始时间，支持日期、日期时间、相对时间 |
| --end-time | 会议结束时间，格式同上 |
| --organizer | 组织者如流imid |
| --participants | 参会人如流imid |

> **获取会议详情**：如需完整详情（参会人、会议纪要），使用 `infoflow-calendar-meeting` skill。

### 周报搜索 (weekly_report_search.py)

**搜索范围**：百度内部周报

| 参数 | 说明 |
|-----|------|
| --query | 检索词（必需） |
| --page | 页码，默认 1 |
| --page-size | 每页数量，默认 20 |
| --start-time | 周报开始时间 |
| --end-time | 周报结束时间 |
| --users | 周报所有者uuap |

> **AI 使用指引**：
> - **分析他人周报** → 使用本技能搜索 + fetch + 分析处理

### 知识库搜索 (ku_search.py)

**搜索范围**：百度知识库(ku.baidu-int.com)文档

| 参数 | 说明 |
|-----|------|
| --word | 查询词（必需） |
| --page | 页码，默认 1 |
| --page-size | 每页大小，默认 10 |
| --repo-guid | 指定知识库搜索 |
| --doc-type | 文档类型：1-文档/4-表格/2-知识本/6-演示文稿 |
| --sort-type | 排序：hot-最热/reme-与我相关 |
| --click-nl-query | 开启自然语言搜索 |

**NL 搜索支持的语义意图**：

| 搜索意图 | 示例 query |
|---|---|
| 找某人写的文档 | `找秋桐写过的文档` |
| 找 IM 中收到的文档 | `找xx发的文档` |
| 找某主题的文档 | `找关于收益回顾的文档` |
| 找自己看过的文档 | `找最近看过的文档` |

### OKR搜索 (okr_search.py)

**搜索范围**：百度内部OKR记录

| 参数 | 说明 |
|-----|------|
| --query | 检索词（必需） |
| --page | 页码，默认 1 |
| --page-size | 每页数量，默认 20 |
| --uids | OKR所有者uid |
| --uuaps | OKR所有者uuap |
| --year | OKR对应年度 |
| --quarter | OKR对应季度：Q1/Q2/Q3/Q4 |

### 通讯录搜索 (address_search.py)

**搜索范围**：百度企业通讯录，支持搜人（corpuser）和搜群（group）

| 参数 | 说明 |
|-----|------|
| --type | 搜索类型（必需）：`corpuser`（搜人）、`group`（搜群） |
| --q | 检索词（必需），支持姓名、邮箱、手机号、群名称等 |

**搜人返回关键字段**：

| 字段 | 说明 |
|-----|------|
| eid | 用户EID（即uuap账号） |
| realname | 真实姓名（可能带 `<em>` 高亮标签） |
| email | 邮箱地址 |
| mobile | 手机号 |
| dept | 部门列表 |
| seatNumber | 座位号 |
| imuid | IM用户ID |

**搜群返回关键字段**：

| 字段 | 说明 |
|-----|------|
| gid | 群组ID |
| name | 群组名称（可能带 `<em>` 高亮标签） |
| desc | 群组描述 |
| gml | 群组人数级别 |
| m_names | 群成员名称列表 |
| user_group_tag | 用户群组标签（如"经常发言"、"今天聊过"） |

> **注意**：返回结果中的 `realname`、`name`、`email`、`m_names` 等字段可能包含 `<em>` 高亮标签，使用时需注意处理。

---

## 详情获取参数

### 内搜详情获取 (neisou_fetch.py)

| 参数 | 说明 |
|-----|------|
| --resource-url | 资源访问URL（必需，从搜索结果获取） |

**返回字段**：content、extJson.resourceName、extJson.description、extJson.resourceUrl

### 周报详情获取 (weekly_report_fetch.py)

| 参数 | 说明 |
|-----|------|
| --uuap | 周报所有者的uuap账号（必需） |
| --date | 日期（必需），支持日期字符串或时间戳 |

**返回字段**：content、extJson.ownerName、extJson.reportName、extJson.subheading

### OKR详情获取 (okr_fetch.py)

| 参数 | 说明 |
|-----|------|
| --uuap | OKR所有者的uuap账号（与--uid二选一） |
| --uid | OKR所有者的uid（与--uuap二选一） |
| --year | 年份（必需） |
| --quarter | 季度：Q1/Q2/Q3/Q4，不传则查询年度OKR |

**返回字段**：data[].ownerName、data[].year、data[].quarter、data[].label、data[].content

---

## 认证配置

本技能使用小龙虾认证，通过 ugate-token 进行鉴权。

- **Token 获取**：仅从本地文件 `~/.config/uuap/.eac_ugate_token_{用户名}` 读取（JSON 取 `token` 字段）；缺失时 `auth.py` **退出码 2**，由 **Agent 先执行** `get-ugate-token` skill，再重试；本 skill **不**内嵌调用其它 skill 脚本
- **用户名获取**：从环境变量 `SANDBOX_USERNAME` 或 `BAIDU_CC_USERNAME` 获取

**环境变量要求**：必须设置 `SANDBOX_USERNAME` 或 `BAIDU_CC_USERNAME`

## 使用技巧

> **重要：命令格式约束**
> 只允许使用单条直接命令，**严禁**以下写法：
> - `export VAR=value && python3 script.py`（设置环境变量再执行）
> - `VAR=value python3 script.py`（行内环境变量赋值）
> - `cd dir && python3 script.py`（切换目录再执行）
> - 任何使用 `&&`、`;`、`|` 等操作符的命令链
>
> 正确方式：直接调用 `python3 scripts/neisou_search.py ...`，环境变量由系统自动注入，路径由脚本内部解析。

---

## Resources

### scripts/
- `neisou_search.py` - 内搜搜索
- `neisou_fetch.py` - 内搜详情获取
- `meeting_search.py` - 会议搜索
- `weekly_report_search.py` - 周报搜索
- `weekly_report_fetch.py` - 周报详情获取
- `ku_search.py` - 知识库搜索
- `okr_search.py` - OKR搜索
- `okr_fetch.py` - OKR详情获取
- `address_search.py` - 通讯录搜索（搜人/搜群）
- `auth.py` - 公共认证模块
- `api_config.py` - API配置模块
- `time_utils.py` - 时间工具模块

### references/
- `api_docs.md` - 5个API的详细接口文档
