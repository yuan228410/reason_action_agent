#!/usr/bin/env python3
"""
OKR详情获取命令行工具。

提供命令行接口调用OKR详情获取API，根据用户uuap或uid、年份和季度获取OKR的详细内容。
"""

import argparse
import json
import sys
import requests
import uuid

# 使用公共模块
from auth import get_fetch_headers
from api_config import OKR_FETCH_URL


def fetch_okr(owner_uuap=None, owner_uid=None, year=None, quarter=None, log_id=None):
    """调用OKR详情获取API。

    Args:
        owner_uuap: OKR所有者的uuap账号（与owner_uid二选一）
        owner_uid: OKR所有者的uid（与owner_uuap二选一）
        year: 年份，如 2026
        quarter: 季度：Q1/Q2/Q3/Q4，查询年度OKR时传空字符串
        log_id: 日志ID，用于链路追踪（可选）

    Returns:
        dict: API响应结果
    """
    headers = get_fetch_headers()

    data = {
        "logId": log_id or str(uuid.uuid4())
    }

    if owner_uuap:
        data["ownerUuap"] = owner_uuap
    if owner_uid:
        data["ownerUid"] = owner_uid
    if year:
        data["year"] = str(year)
    if quarter is not None:  # 允许空字符串
        data["quarter"] = quarter

    try:
        response = requests.post(OKR_FETCH_URL, headers=headers, json=data, timeout=30)
        return response.json()
    except Exception as e:
        return {"code": 500, "message": str(e), "data": None}


def main():
    """主函数，解析命令行参数并执行详情获取。"""
    parser = argparse.ArgumentParser(description="OKR详情获取命令行工具")
    parser.add_argument("--uuap", help="OKR所有者的uuap账号（与--uid二选一）")
    parser.add_argument(
        "--uid", help="OKR所有者的uid（与--uuap二选一，OKR搜索结果中一般包含此字段）"
    )
    parser.add_argument("--year", type=int, required=True, help="年份，如 2026")
    parser.add_argument("--quarter", help="季度：Q1/Q2/Q3/Q4，不传则查询年度OKR")
    parser.add_argument("--log-id", help="日志ID，用于链路追踪")

    args = parser.parse_args()

    if not args.uuap and not args.uid:
        parser.error("必须提供 --uuap 或 --uid 参数")

    result = fetch_okr(
        owner_uuap=args.uuap,
        owner_uid=args.uid,
        year=args.year,
        quarter=args.quarter,
        log_id=args.log_id
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
