#!/usr/bin/env python3
"""
通讯录搜索命令行工具。

提供命令行接口调用通讯录搜索API，支持搜人（corpuser）和搜群（group）。
"""

import argparse
import json
import sys
import requests

# 使用公共模块
from auth import get_fetch_headers
from api_config import ADDRESS_SEARCH_URL


def search_address(search_type, query):
    """调用通讯录搜索API。

    Args:
        search_type: 搜索类型，corpuser（搜人）或 group（搜群）
        query: 检索词

    Returns:
        dict: API响应结果
    """
    headers = get_fetch_headers()

    data = {
        "type": search_type,
        "q": query
    }

    try:
        response = requests.post(ADDRESS_SEARCH_URL, headers=headers, json=data, timeout=30)
        return response.json()
    except Exception as e:
        return {"code": 500, "message": str(e), "data": None}


def main():
    """主函数，解析命令行参数并执行搜索。"""
    parser = argparse.ArgumentParser(description="通讯录搜索命令行工具（搜人/搜群）")
    parser.add_argument("--type", required=True, choices=["corpuser", "group"],
                        help="搜索类型：corpuser（搜人）、group（搜群）")
    parser.add_argument("--q", required=True, help="检索词，支持姓名、邮箱、手机号、群名称等")

    args = parser.parse_args()

    result = search_address(
        search_type=args.type,
        query=args.q
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
