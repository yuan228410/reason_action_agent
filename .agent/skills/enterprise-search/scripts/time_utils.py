#!/usr/bin/env python3
"""
时间参数处理工具 - 企业搜索所有脚本共享。

统一处理时间参数的解析，支持多种格式和相对时间。
解决不同脚本时间戳单位不一致的问题。
"""

from datetime import datetime, timedelta
from typing import Union


# 时间单位常量
UNIT_SECONDS = "s"      # 秒
UNIT_MILLISECONDS = "ms"  # 毫秒


def parse_time(time_str: str, unit: str = UNIT_MILLISECONDS) -> int:
    """统一时间解析接口

    支持多种时间格式和相对时间表达。

    Args:
        time_str: 时间字符串，支持格式：
            - 纯数字：直接当作时间戳
            - 日期：2026-03-16、2026/03/16
            - 日期时间：2026-03-16 09:00、2026-03-16 09:00:00
            - 相对时间：today, yesterday, last_week, this_week, last_month
        unit: 输出单位，"ms"（毫秒，默认）或 "s"（秒）

    Returns:
        时间戳（按指定单位）

    Raises:
        ValueError: 无法解析时间字符串

    Examples:
        >>> parse_time("2026-03-16")  # 毫秒时间戳
        >>> parse_time("2026-03-16 09:00", unit="s")  # 秒时间戳
        >>> parse_time("last_week", unit="s")  # 上周一的秒时间戳
    """
    if not time_str:
        raise ValueError("时间字符串不能为空")

    # 纯数字，直接返回
    if time_str.isdigit():
        return int(time_str)

    # 相对时间处理
    dt = _parse_relative_time(time_str)
    if dt is None:
        # 解析日期时间格式
        dt = _parse_datetime(time_str)
        if dt is None:
            raise ValueError(
                f"无法解析时间 '{time_str}'\n"
                f"支持格式：\n"
                f"  - 日期：2026-03-16、2026/03/16\n"
                f"  - 日期时间：2026-03-16 09:00、2026-03-16 09:00:00\n"
                f"  - 相对时间：today、yesterday、last_week、this_week、last_month\n"
                f"  - 时间戳：纯数字"
            )

    # 转换为时间戳
    timestamp = int(dt.timestamp())
    return timestamp * 1000 if unit == UNIT_MILLISECONDS else timestamp


def _parse_relative_time(time_str: str) -> datetime:
    """解析相对时间

    Args:
        time_str: 相对时间字符串

    Returns:
        datetime 对象，如果不是相对时间返回 None
    """
    time_lower = time_str.lower().strip()

    now = datetime.now()

    relative_times = {
        "today": now.replace(hour=0, minute=0, second=0, microsecond=0),
        "yesterday": (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0),
        "this_week": _get_week_start(now),
        "last_week": _get_week_start(now) - timedelta(weeks=1),
        "this_month": now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
        "last_month": _get_last_month_start(now),
    }

    return relative_times.get(time_lower)


def _parse_datetime(time_str: str) -> datetime:
    """解析日期时间格式

    Args:
        time_str: 日期时间字符串

    Returns:
        datetime 对象，解析失败返回 None
    """
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue

    return None


def _get_week_start(dt: datetime) -> datetime:
    """获取所在周的周一

    Args:
        dt: 日期时间

    Returns:
        所在周周一 00:00:00
    """
    days_since_monday = dt.weekday()
    monday = dt - timedelta(days=days_since_monday)
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def _get_last_month_start(dt: datetime) -> datetime:
    """获取上月第一天

    Args:
        dt: 日期时间

    Returns:
        上月第一天 00:00:00
    """
    first_of_this_month = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_of_last_month = first_of_this_month - timedelta(days=1)
    return last_of_last_month.replace(day=1)


# ============ 便捷函数，兼容旧代码 ============

def parse_time_to_seconds(time_str: str) -> int:
    """解析时间为秒时间戳（兼容旧函数名）

    Args:
        time_str: 时间字符串

    Returns:
        秒时间戳
    """
    return parse_time(time_str, unit=UNIT_SECONDS)


def parse_time_to_milliseconds(time_str: str) -> int:
    """解析时间为毫秒时间戳（兼容旧函数名）

    Args:
        time_str: 时间字符串

    Returns:
        毫秒时间戳
    """
    return parse_time(time_str, unit=UNIT_MILLISECONDS)


# ============ 时间范围计算 ============

def get_time_range(range_type: str, unit: str = UNIT_MILLISECONDS) -> tuple:
    """获取时间范围

    Args:
        range_type: 时间范围类型：
            - "today": 今天
            - "yesterday": 昨天
            - "this_week": 本周
            - "last_week": 上周
            - "this_month": 本月
            - "last_month": 上月
        unit: 时间戳单位

    Returns:
        (start_time, end_time) 元组
    """
    now = datetime.now()

    ranges = {
        "today": (
            now.replace(hour=0, minute=0, second=0, microsecond=0),
            now.replace(hour=23, minute=59, second=59, microsecond=999999)
        ),
        "yesterday": (
            (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0),
            (now - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
        ),
        "this_week": (
            _get_week_start(now),
            _get_week_start(now) + timedelta(days=6, hours=23, minutes=59, seconds=59)
        ),
        "last_week": (
            _get_week_start(now) - timedelta(weeks=1),
            _get_week_start(now) - timedelta(seconds=1)
        ),
        "this_month": (
            now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            (now.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        ),
        "last_month": (
            _get_last_month_start(now),
            now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=1)
        ),
    }

    if range_type not in ranges:
        raise ValueError(f"未知的时间范围类型: {range_type}，可选: {list(ranges.keys())}")

    start, end = ranges[range_type]
    multiplier = 1000 if unit == UNIT_MILLISECONDS else 1

    return int(start.timestamp() * multiplier), int(end.timestamp() * multiplier)


if __name__ == "__main__":
    # 测试
    print("时间工具测试:")
    print(f"  today (ms): {parse_time('today')}")
    print(f"  yesterday (s): {parse_time('yesterday', unit='s')}")
    print(f"  last_week (ms): {parse_time('last_week')}")
    print(f"  2026-03-16 (ms): {parse_time('2026-03-16')}")
    print(f"  2026-03-16 09:00 (s): {parse_time('2026-03-16 09:00', unit='s')}")

    print("\n时间范围测试:")
    start, end = get_time_range("last_week", unit="s")
    print(f"  last_week range (s): {start} - {end}")
