#!/usr/bin/env python3
"""
周报搜索命令行工具。

提供命令行接口调用周报搜索API，搜索百度内部周报。
"""

import argparse
import json
import sys
import requests
import uuid

# 使用公共模块
from auth import get_auth_headers
from api_config import WEEKLY_REPORT_SEARCH_URL
from time_utils import parse_time, UNIT_MILLISECONDS


def search_weekly_report(query, page_no=1, page_size=20, show_type="flat",
                         start_time=None, end_time=None, users=None):
    """调用周报搜索API。
    
    Args:
        query: 检索词
        page_no: 页码，默认1
        page_size: 每页数量，默认20
        show_type: 展现形式，默认"flat"
        start_time: 周报开始时间（毫秒时间戳）
        end_time: 周报结束时间（毫秒时间戳）
        users: 周报所有者uuap
    
    Returns:
        dict: API响应结果
    """
    headers = get_auth_headers()
    
    data = {
        "query": query,
        "pageNo": page_no,
        "pageSize": page_size,
        "showType": show_type,
        "logId": str(uuid.uuid4())
    }
    
    if start_time:
        data["startTime"] = start_time
    if end_time:
        data["endTime"] = end_time
    if users:
        data["users"] = users
    
    try:
        response = requests.post(WEEKLY_REPORT_SEARCH_URL, headers=headers, json=data, timeout=30)
        return response.json()
    except Exception as e:
        return {"code": 500, "message": str(e), "data": None}


def main():
    """主函数，解析命令行参数并执行搜索。"""
    parser = argparse.ArgumentParser(description="周报搜索命令行工具")
    parser.add_argument("--query", required=True, help="检索词")
    parser.add_argument("--page", type=int, default=1, help="页码，默认 1")
    parser.add_argument("--page-size", type=int, default=20, help="每页数量，默认 20")
    parser.add_argument("--show-type", default="flat", help="展现形式：flat/collapse")
    parser.add_argument("--start-time", help="周报开始时间，支持日期(2026-03-16)、日期时间(2026-03-16 09:00)、相对时间(last_week)或毫秒时间戳")
    parser.add_argument("--end-time", help="周报结束时间，格式同上")
    parser.add_argument("--users", help="周报所有者uuap")

    args = parser.parse_args()

    # 使用统一的时间解析函数（毫秒时间戳）
    start_time = parse_time(args.start_time, unit=UNIT_MILLISECONDS) if args.start_time else None
    end_time = parse_time(args.end_time, unit=UNIT_MILLISECONDS) if args.end_time else None

    result = search_weekly_report(
        query=args.query,
        page_no=args.page,
        page_size=args.page_size,
        show_type=args.show_type,
        start_time=start_time,
        end_time=end_time,
        users=args.users
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
