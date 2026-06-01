#!/usr/bin/env python3
"""
内搜详情获取命令行工具。

提供命令行接口调用Solr详情获取API，根据资源URL获取内搜搜索结果的完整内容。
仅适用于内搜搜索结果中 resultType 为 0 的结果。
"""

import argparse
import json
import sys
import requests
import uuid

# 使用公共模块
from auth import get_fetch_headers
from api_config import NEISOU_FETCH_URL


def fetch_solr(resource_url, log_id=None):
    """调用Solr详情获取API。

    Args:
        resource_url: 资源访问URL
        log_id: 日志ID，用于链路追踪（可选）

    Returns:
        dict: API响应结果
    """
    headers = get_fetch_headers()

    data = {
        "resourceUrl": resource_url,
        "logId": log_id or str(uuid.uuid4())
    }

    try:
        response = requests.post(NEISOU_FETCH_URL, headers=headers, json=data, timeout=30)
        return response.json()
    except Exception as e:
        return {"code": 500, "message": str(e), "data": None}


def main():
    """主函数，解析命令行参数并执行详情获取。"""
    parser = argparse.ArgumentParser(description="内搜详情获取命令行工具（Solr）")
    parser.add_argument("--resource-url", required=True, help="资源访问URL（从内搜搜索结果中获取）")
    parser.add_argument("--log-id", help="日志ID，用于链路追踪")

    args = parser.parse_args()

    result = fetch_solr(
        resource_url=args.resource_url,
        log_id=args.log_id
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
