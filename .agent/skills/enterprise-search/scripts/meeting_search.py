#!/usr/bin/env python3
"""
会议搜索命令行工具。

提供命令行接口调用会议搜索API，搜索百度内部会议记录。
"""

import argparse
import json
import sys
import requests
import uuid

# 使用公共模块
from auth import get_auth_headers
from api_config import MEETING_SEARCH_URL
from time_utils import parse_time, UNIT_SECONDS


def search_meeting(q, page_no=1, page_size=20, filter_type="no",
                   start_time=None, end_time=None, content_type=None,
                   organizer=None, participants=None, can_search_doc=False):
    """调用会议搜索API。
    
    Args:
        q: 检索词
        page_no: 页码，默认1
        page_size: 每页数量，默认20
        filter_type: 筛选器类别，默认"no"
        start_time: 会议开始时间（秒时间戳）
        end_time: 会议结束时间（秒时间戳）
        content_type: 检索内容筛选
        organizer: 组织者如流imid
        participants: 参会人如流imid
        can_search_doc: 是否搜索文档，默认False
    
    Returns:
        dict: API响应结果
    """
    headers = get_auth_headers()
    
    data = {
        "q": q,
        "pageNo": page_no,
        "pageSize": page_size,
        "filter": filter_type,
        "logId": str(uuid.uuid4())
    }
    
    if start_time:
        data["startTime"] = start_time
    if end_time:
        data["endTime"] = end_time
    if content_type:
        data["contentType"] = content_type
    if organizer:
        data["organizer"] = organizer
    if participants:
        data["participants"] = participants
    if can_search_doc:
        data["canSearchDoc"] = True
    
    try:
        response = requests.post(MEETING_SEARCH_URL, headers=headers, json=data, timeout=30)
        return response.json()
    except Exception as e:
        return {"code": 500, "message": str(e), "data": None}


def main():
    """主函数，解析命令行参数并执行搜索。"""
    parser = argparse.ArgumentParser(description="会议搜索命令行工具")
    parser.add_argument("--q", required=True, help="检索词")
    parser.add_argument("--page", type=int, default=1, help="页码，默认 1")
    parser.add_argument("--page-size", type=int, default=20, help="每页数量，默认 20")
    parser.add_argument("--filter", default="no", help="筛选器类别")
    parser.add_argument("--start-time", help="会议开始时间，支持日期(2026-03-16)、日期时间(2026-03-16 09:00)、相对时间(last_week)或秒时间戳")
    parser.add_argument("--end-time", help="会议结束时间，格式同上")
    parser.add_argument("--content-type", help="检索内容筛选")
    parser.add_argument("--organizer", help="组织者如流imid")
    parser.add_argument("--participants", help="参会人如流imid")
    parser.add_argument("--no-doc", action="store_true", help="不搜索文档")
    
    args = parser.parse_args()
    
    # 使用统一的时间解析函数（秒时间戳）
    start_time = parse_time(args.start_time, unit=UNIT_SECONDS) if args.start_time else None
    end_time = parse_time(args.end_time, unit=UNIT_SECONDS) if args.end_time else None

    result = search_meeting(
        q=args.q,
        page_no=args.page,
        page_size=args.page_size,
        filter_type=args.filter,
        start_time=start_time,
        end_time=end_time,
        content_type=args.content_type,
        organizer=args.organizer,
        participants=args.participants,
        can_search_doc=not args.no_doc
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
