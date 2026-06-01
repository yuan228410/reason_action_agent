#!/usr/bin/env python3
"""
OKR搜索命令行工具。

提供命令行接口调用OKR搜索API，搜索百度内部OKR记录。
"""

import argparse
import json
import sys
import requests
import uuid

# 使用公共模块
from auth import get_auth_headers
from api_config import OKR_SEARCH_URL


def search_okr(query, page_no=1, page_size=20, uids=None, uuaps=None, 
              year=None, quarter=None):
    """调用OKR搜索API。
    
    Args:
        query: 检索词
        page_no: 页码，默认1
        page_size: 每页数量，默认20
        uids: OKR所有者uid
        uuaps: OKR所有者uuap
        year: OKR对应年度
        quarter: OKR对应季度：Q1/Q2/Q3/Q4
    
    Returns:
        dict: API响应结果
    """
    headers = get_auth_headers()
    
    data = {
        "query": query,
        "pageNo": page_no,
        "pageSize": page_size,
        "logId": str(uuid.uuid4())
    }
    
    if uids:
        data["uids"] = uids
    if uuaps:
        data["uuaps"] = uuaps
    if year:
        data["year"] = year
    if quarter:
        data["quarter"] = quarter
    
    try:
        response = requests.post(OKR_SEARCH_URL, headers=headers, json=data, timeout=30)
        return response.json()
    except Exception as e:
        return {"code": 500, "message": str(e), "data": None}


def main():
    """主函数，解析命令行参数并执行搜索。"""
    parser = argparse.ArgumentParser(description="OKR搜索命令行工具")
    parser.add_argument("--query", required=True, help="检索词")
    parser.add_argument("--page", type=int, default=1, help="页码，默认 1")
    parser.add_argument("--page-size", type=int, default=20, help="每页数量，默认 20")
    parser.add_argument("--uids", help="OKR所有者uid")
    parser.add_argument("--uuaps", help="OKR所有者uuap")
    parser.add_argument("--year", type=int, help="OKR对应年度")
    parser.add_argument("--quarter", help="OKR对应季度：Q1/Q2/Q3/Q4")
    
    args = parser.parse_args()
    
    result = search_okr(
        query=args.query,
        page_no=args.page,
        page_size=args.page_size,
        uids=args.uids,
        uuaps=args.uuaps,
        year=args.year,
        quarter=args.quarter
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
