#!/usr/bin/env python3
"""
内搜搜索命令行工具。

提供命令行接口调用内搜搜索API，搜索百度内部知识文档、百科、课程等资源。
"""

import argparse
import json
import sys
import requests
import uuid

# 使用公共模块
from auth import get_auth_headers
from api_config import NEISOU_SEARCH_URL


def search_neisou(word, page_no=1, with_auth=True):
    """调用内搜搜索API。
    
    Args:
        word: 搜索关键词
        page_no: 页码，默认1
        with_auth: 是否带权限过滤，默认True
    
    Returns:
        dict: API响应结果
    """
    headers = get_auth_headers()
    
    data = {
        "word": word,
        "pageNo": page_no,
        "auth": not with_auth
    }
    
    try:
        response = requests.post(NEISOU_SEARCH_URL, headers=headers, json=data, timeout=30)
        return response.json()
    except Exception as e:
        return {"code": 500, "message": str(e), "data": None}


def main():
    """主函数，解析命令行参数并执行搜索。"""
    parser = argparse.ArgumentParser(description="内搜搜索命令行工具")
    parser.add_argument("--word", required=True, help="搜索关键词")
    parser.add_argument("--page", type=int, default=1, help="页码，默认 1")
    parser.add_argument("--no-auth", action="store_true", help="不带权限过滤")
    
    args = parser.parse_args()
    
    result = search_neisou(
        word=args.word,
        page_no=args.page,
        with_auth=not args.no_auth
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
