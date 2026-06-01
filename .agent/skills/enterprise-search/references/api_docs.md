# 企业搜索 API 详细文档

## 目录

1. [内搜搜索](#内搜搜索)
2. [会议搜索](#会议搜索)
3. [周报搜索](#周报搜索)
4. [知识库搜索](#知识库搜索)
5. [OKR搜索](#okr搜索)
6. [通讯录搜索](#通讯录搜索)
7. [周报详情获取](#周报详情获取)
8. [内搜详情获取](#内搜详情获取)
9. [OKR详情获取](#okr详情获取)

---

## 内搜搜索

### 接口信息

|项目|说明|
|-|-|
|接口名称|内搜搜索|
|请求方式|POST|
|请求地址|`/openapi/search/neisou`|

### 请求头

|参数名|是否必须|参数说明|
|-|-|-|
|Content-Type|是|application/json|
|ugate-token|是|身份验证Token|
|uuap|是|当前登录用户的uuap|

### 请求参数

|参数名|是否必须|类型|说明|
|-|-|-|-|
|word|是|String|查询词|
|pageNo|否|Integer|页码，默认1|
|auth|否|Boolean|是否带权限过滤：true-不带权限，false-带权限（默认）|

### 响应示例

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "data": [...]
    }
}
```

---

## 会议搜索

### 接口信息

|项目|说明|
|-|-|
|接口名称|会议搜索|
|请求方式|POST|
|请求地址|`/openapi/search/meeting`|

### 请求头

|参数名|是否必须|参数说明|
|-|-|-|
|Content-Type|是|application/json|
|ugate-token|是|身份验证Token|
|uuap|是|当前登录用户的uuap|

### 请求参数

|参数名|是否必须|类型|说明|
|-|-|-|-|
|q|是|String|检索词|
|pageNo|是|Integer|页码|
|pageSize|是|Integer|每页数量|
|filter|是|String|筛选器类别：no/time/contentType/meetingType/organizer/participants|
|startTime|否|Long|会议开始时间（秒时间戳）|
|endTime|否|Long|会议结束时间（秒时间戳）|
|contentType|否|String|检索内容筛选：title/summary/record/docTitle|
|organizer|否|String|组织者如流imid|
|participants|否|String|参会人如流imid|
|canSearchDoc|否|Boolean|是否搜索文档|

### 响应示例

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "data": [...]
    }
}
```

---

## 周报搜索

### 接口信息

|项目|说明|
|-|-|
|接口名称|周报搜索|
|请求方式|POST|
|请求地址|`/openapi/search/weeklyReport`|

### 请求头

|参数名|是否必须|参数说明|
|-|-|-|
|Content-Type|是|application/json|
|ugate-token|是|身份验证Token|
|uuap|是|当前登录用户的uuap|

### 请求参数

|参数名|是否必须|类型|说明|
|-|-|-|-|
|query|是|String|检索词|
|pageNo|是|Integer|页码|
|pageSize|是|Integer|每页数量|
|showType|是|String|展现形式：flat/collapse|
|startTime|否|Long|周报开始时间（毫秒时间戳）|
|endTime|否|Long|周报结束时间（毫秒时间戳）|
|users|否|String|周报所有者uuap|

### 响应示例

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "data": [
            {
                "weeklyId": "xxx",
                "ownerName": "张三",
                "uuapUser": "zhangsan",
                "title": "第12周周报",
                "content": "本周工作...",
                "url": "https://..."
            }
        ]
    }
}
```

---

## 知识库搜索

### 接口信息

|项目|说明|
|-|-|
|接口名称|知识库搜索|
|请求方式|POST|
|请求地址|`/openapi/search/kuweb`|

### 请求头

|参数名|是否必须|参数说明|
|-|-|-|
|Content-Type|是|application/json|
|ugate-token|是|身份验证Token|
|uuap|是|当前登录用户的uuap|

### 请求参数

|参数名|是否必须|类型|说明|
|-|-|-|-|
|word|是|String|查询词|
|pageNo|是|Integer|页码|
|pageSize|是|Integer|每页大小|
|isClickNlQuery|是|Boolean|是否点击自然语言查询|
|filters|是|Map|过滤条件（sortType必传）|

### filters

|参数名|是否必须|类型|说明|
|-|-|-|-|
|sortType|是|String|排序方式：hot-最热、reme-与我相关|
|repoGuid|否|List<String>|指定知识库搜索|
|docType|否|List<String>|文档类型：1-文档/4-表格/2-知识本/6-演示文稿/-1-知识库|

### 响应示例

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "data": [
            {
                "docGuid": "xxx",
                "title": "文档标题",
                "content": "文档摘要",
                "url": "https://ku.baidu-int.com/..."
            }
        ]
    }
}
```

---

## OKR搜索

### 接口信息

|项目|说明|
|-|-|
|接口名称|OKR搜索|
|请求方式|POST|
|请求地址|`/openapi/search/okr`|

### 请求头

|参数名|是否必须|参数说明|
|-|-|-|
|Content-Type|是|application/json|
|ugate-token|是|身份验证Token|
|uuap|是|当前登录用户的uuap|

### 请求参数

|参数名|是否必须|类型|说明|
|-|-|-|-|
|query|是|String|检索词|
|pageNo|是|Integer|页码|
|pageSize|是|Integer|每页数量|
|uids|否|String|OKR所有者uid|
|uuaps|否|String|OKR所有者uuap|
|year|否|Integer|OKR对应年度|
|quarter|否|String|OKR对应季度：Q1/Q2/Q3/Q4|

### 响应示例

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "data": [
            {
                "year": 2026,
                "quarter": "Q1",
                "title": "xxx的OKR",
                "content": "O1:xxx\nKR1:xxx",
                "url": "https://okr.baidu-int.com/..."
            }
        ]
    }
}
```

---

## 通讯录搜索

### 接口信息

|项目|说明|
|-|-|
|接口名称|通讯录搜索|
|请求方式|POST|
|请求地址|`/openapi/search/query`|

### 请求头

|参数名|是否必须|参数说明|
|-|-|-|
|Content-Type|是|application/json|
|Ugate-Token|是|身份验证Token|
|uuap|是|当前登录用户的uuap|

### 请求参数

|参数名|是否必须|类型|说明|
|-|-|-|-|
|type|是|String|搜索类型：corpuser（企业用户）、group（群组）|
|q|是|String|检索词，支持姓名、邮箱、手机号、群名称等|

### type=corpuser 时 data.data

|参数名|类型|说明|
|-|-|-|
|total|Integer|总结果数|
|items|Array|用户列表|

### data.data.items[]（用户）

|参数名|类型|说明|
|-|-|-|
|eid|String|用户EID（即uuap账号）|
|name|String|用户名称（百度账号）|
|realname|String|真实姓名（可能带 `<em>` 高亮标签）|
|email|String|邮箱地址（可能带 `<em>` 高亮标签）|
|mobile|String|手机号|
|dept|Array|部门列表|
|seatNumber|String|座位号|
|imuid|Long|IM用户ID|
|leave|String|是否离职（0-在职，1-离职）|
|type|String|用户类型|
|picurl|String|头像URL|
|corpid|String|公司ID|

### type=group 时 data.data.group

|参数名|类型|说明|
|-|-|-|
|total|Integer|群组总数量|
|page|Integer|当前页码|
|pageSize|Integer|每页数量|
|items|Array|群组列表|

### data.data.group.items[]（群组）

|参数名|类型|说明|
|-|-|-|
|gid|Long|群组ID|
|name|String|群组名称（可能带 `<em>` 高亮标签）|
|desc|String|群组描述|
|gml|String|群组人数级别|
|corpid|String|公司ID|
|atime|String|最后活跃时间（时间戳）|
|ctime|String|创建时间（时间戳）|
|m_names|Array|群成员名称列表|
|user_group_tag|String|用户群组标签（如"经常发言"）|

### 响应示例

#### type=corpuser 成功响应

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "data": {
            "total": 3,
            "items": [
                {
                    "eid": "panqiutong",
                    "name": "QTmira",
                    "realname": "潘<em>秋桐</em>",
                    "email": "panqiutong@baidu.com",
                    "mobile": "+86 17600104107",
                    "dept": ["超级助理与AI组件平台组"],
                    "seatNumber": "BD-F2-CE-442",
                    "imuid": 1396227307,
                    "leave": "0"
                }
            ]
        }
    }
}
```

#### type=group 成功响应

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "data": {
            "group": {
                "total": 141,
                "page": 1,
                "pageSize": 20,
                "items": [
                    {
                        "gid": 12589166,
                        "name": "Skills小分队",
                        "desc": "",
                        "gml": "9",
                        "m_names": ["潘<em>秋桐</em>"],
                        "user_group_tag": "经常发言"
                    }
                ]
            }
        }
    }
}
```

> **注意**：返回结果中的 `realname`、`name`、`email`、`m_names` 等字段可能包含 `<em>` 高亮标签，使用时需注意处理。

---

## 周报详情获取

### 接口信息

|项目|说明|
|-|-|
|接口名称|周报详情获取|
|请求方式|POST|
|请求地址|`/openapi/fetch/weeklyReport`|

### 请求头

|参数名|是否必须|参数说明|
|-|-|-|
|Content-Type|是|application/json|
|Ugate-Token|是|身份验证Token|
|uuap|是|当前登录用户的uuap|

### 请求参数

|参数名|是否必须|类型|说明|
|-|-|-|-|
|uuap|是|String|周报所有者的uuap账号|
|date|是|Long|周报时间戳（毫秒时间戳）|
|logId|否|String|日志ID，用于链路追踪|

### 响应参数

|参数名|类型|说明|
|-|-|-|
|code|Integer|状态码，0为成功|
|message|String|状态信息|
|data|Object|响应数据|

#### data

|参数名|类型|说明|
|-|-|-|
|content|String|周报详细内容（JSON字符串格式，需二次解析）|
|extJson|Object|扩展信息对象|

#### extJson

|参数名|类型|说明|
|-|-|-|
|weeklyUrl|String|周报链接地址（可能为null）|
|ownerName|String|周报所有者姓名|
|reportName|String|周报名称，格式：部门-姓名 周报|
|uuap|String|周报所有者的uuap账号|
|startTime|Long|周报开始时间（毫秒时间戳）|
|ownerId|String|周报所有者ID|
|subheading|String|周报时间段，如 "2026年03月16日~03月22日"|
|infoflowTitle|String|信息流标题，通常为 "姓名的周报"|

### 响应示例

成功：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "content": "[\"主线工作\\n主线（优先级排序）\\n整体进展/现状\\n关键里程碑\\n本周工作\\nC端Skills建设\\n已接入skill：PPT生成、信息图生成...\\n\\n风险及问题\\n\\n\"]",
        "extJson": {
            "weeklyUrl": null,
            "ownerName": "黄凯健",
            "reportName": "超级助理与AI组件平台组-黄凯健 周报",
            "uuap": "huangkaijian",
            "startTime": 1773998630024,
            "ownerId": "1103145",
            "subheading": "2026年03月16日~03月22日",
            "infoflowTitle": "黄凯健的周报"
        }
    }
}
```

失败：

```json
{
    "code": 500,
    "message": "周报详情获取异常: xxx",
    "data": null
}
```

> **注意**：`content` 字段为 JSON 字符串格式（被转义的JSON数组），需要二次解析获取周报详细内容。

---

## 内搜详情获取

针对内搜搜索结果中 resultType 为 0/3 的结果，该接口支持获取完整内容。

### 接口信息

|项目|说明|
|-|-|
|接口名称|Solr详情获取|
|请求方式|POST|
|请求地址|`/openapi/fetch/solr`|

### 请求头

|参数名|是否必须|参数说明|
|-|-|-|
|Content-Type|是|application/json|
|Ugate-Token|是|身份验证Token|
|uuap|是|当前登录用户的uuap|

### 请求参数

|参数名|是否必须|类型|说明|
|-|-|-|-|
|resourceUrl|是|String|资源访问URL，用于Solr url字段精确查询|
|logId|否|String|日志ID，用于链路追踪|

### 响应参数

|参数名|类型|说明|
|-|-|-|
|code|Integer|状态码，0为成功|
|message|String|状态信息|
|data|Object|响应数据|

#### data

|参数名|类型|说明|
|-|-|-|
|content|String|正文内容|
|extJson|Object|扩展信息对象|

#### extJson

|参数名|类型|说明|
|-|-|-|
|resourceName|String|资源名称（优先使用Solr返回的title）|
|description|String|描述/摘要|
|resourceUrl|String|实际命中的URL|

### 响应示例

成功：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "content": "[\"创建软链接 本接口用于为BOS中相同bucket下已有的目的object创建软链接...\"]",
        "extJson": {
            "resourceUrl": "https://cloud.baidu.com/doc/BOS/s/Fl5jh33lb",
            "description": "BOS软链接文档",
            "resourceName": "软链接"
        }
    }
}
```

无数据：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "content": "",
        "extJson": {
            "resourceUrl": "https://xxx.com/not-exist",
            "description": null,
            "resourceName": ""
        }
    }
}
```

失败：

```json
{
    "code": 400,
    "message": "resourceUrl不能为空",
    "data": null
}
```

> **注意**：
> - 查询时优先使用 HTTPS 格式 URL，如果未命中会自动降级为 HTTP 重试
> - Solr 返回的 title 会优先作为 resourceName
> - 如果 Solr 和 description 都无内容，返回空字符串 content
> - content 可能是 JSON 数组格式的字符串，需要二次解析

---

## OKR详情获取

### 接口信息

|项目|说明|
|-|-|
|接口名称|OKR详情获取|
|请求方式|POST|
|请求地址|`/openapi/fetch/okr`|

### 请求头

|参数名|是否必须|参数说明|
|-|-|-|
|Content-Type|是|application/json|
|Ugate-Token|是|身份验证Token|
|uuap|是|当前登录用户的uuap|

### 请求参数

|参数名|是否必须|类型|说明|
|-|-|-|-|
|ownerUuap|与ownerUid二选一|String|OKR所有者的uuap账号，优先使用|
|ownerUid|与ownerUuap二选一|String|OKR所有者的uid|
|year|是|String|年份，如 "2026"|
|quarter|否|String|季度：Q1/Q2/Q3/Q4，查询年度OKR时传空字符串|
|logId|否|String|日志ID，用于链路追踪|

### 响应参数

|参数名|类型|说明|
|-|-|-|
|code|Integer|状态码，0为成功|
|message|String|状态信息|
|data|Object|响应数据|

#### data

|参数名|类型|说明|
|-|-|-|
|data|Array|OKR列表数组|
|extJson|Object|扩展信息对象|

#### data 数组元素

|参数名|类型|说明|
|-|-|-|
|ownerName|String|OKR所有者姓名|
|year|String|年份|
|quarter|String|季度|
|label|String|OKR标签，如 O1、O1.KR1、O2 等|
|content|String|OKR内容描述|

#### extJson

|参数名|类型|说明|
|-|-|-|
|resourceUrl|String|OKR页面链接|
|year|String|年份|
|quarter|String|季度|
|ownerUuap|String|OKR所有者uuap|

### 响应示例

成功：

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "data": [
            {
                "ownerName": "黄凯健",
                "year": "2026",
                "quarter": "Q1",
                "label": "O1",
                "content": "【基础能力建设】通过能力优化赋能 AI 搜索与传统搜索，促进用户搜索满足率整体提升"
            },
            {
                "ownerName": "黄凯健",
                "year": "2026",
                "quarter": "Q1",
                "label": "O1.KR1",
                "content": "【权威质量特征】建立权威语义库，优化召回排序效果"
            }
        ],
        "extJson": {
            "resourceUrl": "https://okr.baidu-int.com/personOkr?ownerId=1103145&year=2026&quarter=Q1",
            "year": "2026",
            "quarter": "Q1",
            "ownerUuap": "huangkaijian"
        }
    }
}
```

无数据：

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "content": "",
        "extJson": {
            "year": "2025",
            "quarter": "Q2",
            "ownerUuap": "lisi",
            "resourceUrl": ""
        }
    }
}
```

失败：

```json
{
    "code": 500,
    "message": "OKR详情获取异常: xxx",
    "data": null
}
```

> **注意**：
> - `label` 以 "O" 开头表示目标（Objective），以 "O数字.KR数字" 表示关键结果（Key Result）
> - 同一目标下的 KR 使用相同的 O 编号前缀（如 O1.KR1、O1.KR2 都属于 O1）
