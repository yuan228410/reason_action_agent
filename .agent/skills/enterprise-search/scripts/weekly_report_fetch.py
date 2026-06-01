#!/usr/bin/env python3
"""
周报详情获取命令行工具。

提供命令行接口调用周报详情获取API，根据uuap和日期获取指定周报的详细内容。
"""

import argparse
import json
import sys
import requests
import uuid

# 使用公共模块
from auth import get_fetch_headers
from api_config import WEEKLY_REPORT_FETCH_URL
from time_utils import parse_time, UNIT_MILLISECONDS


def fetch_weekly_report(uuap, date, log_id=None):
    """调用周报详情获取API。

    Args:
        uuap: 周报所有者的uuap账号
        date: 日期（毫秒时间戳或日期字符串）
        log_id: 日志ID，用于链路追踪（可选）

    Returns:
        dict: API响应结果
    """
    headers = get_fetch_headers()

    # 计算周报时间戳：该周周一中午12点
    # 传入的日期会被转换为该周周一中午12点的时间戳
    date_ts = date if isinstance(date, int) else parse_time(date, unit=UNIT_MILLISECONDS)

    data = {
        "uuap": uuap,
        "date": date_ts,
        "logId": log_id or str(uuid.uuid4())
    }

    try:
        response = requests.post(WEEKLY_REPORT_FETCH_URL, headers=headers, json=data, timeout=30)
        return response.json()
    except Exception as e:
        return {"code": 500, "message": str(e), "data": None}


def main():
    """主函数，解析命令行参数并执行详情获取。"""
    parser = argparse.ArgumentParser(description="周报详情获取命令行工具")
    parser.add_argument("--uuap", required=True, help="周报所有者的uuap账号")
    parser.add_argument(
        "--date", required=True,
        help="日期。支持日期字符串（如 2026-03-16、2026/03/16）或毫秒时间戳。"
             "传入该周内任意一个工作日的日期即可，脚本会自动转换为该周周一中午12点的时间戳"
    )
    parser.add_argument("--log-id", help="日志ID，用于链路追踪")

    args = parser.parse_args()

    result = fetch_weekly_report(
        uuap=args.uuap,
        date=args.date,
        log_id=args.log_id
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
