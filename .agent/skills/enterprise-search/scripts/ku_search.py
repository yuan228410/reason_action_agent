#!/usr/bin/env python3
"""
知识库搜索命令行工具。

提供命令行接口调用知识库搜索API，搜索百度内部知识库文档。
"""

import argparse
import json
import sys
import requests
import uuid

# 使用公共模块
from auth import get_auth_headers
from api_config import KU_SEARCH_URL


def search_ku(word, page_no=1, page_size=10,
              repo_guid=None, doc_type=None, sort_type="reme",
              is_click_nl_query=False):
    """调用知识库搜索API。
    
    Args:
        word: 查询词
        page_no: 页码，默认1
        page_size: 每页大小，默认10
        repo_guid: 指定知识库搜索
        doc_type: 文档类型
        sort_type: 排序方式，默认"reme"（与我相关），可选"hot"（最热）
        is_click_nl_query: 是否使用自然语言查询，默认False
    
    Returns:
        dict: API响应结果
    """
    headers = get_auth_headers()
    headers["Content-Type"] = "application/json; charset=utf-8"
    
    if is_click_nl_query:
        sort_type = "reme"
    
    data = {
        "word": word,
        "pageNo": page_no,
        "pageSize": page_size,
        "queryId": str(uuid.uuid4()),
        "searchId": str(uuid.uuid4()),
        "isClickNlQuery": is_click_nl_query,
        "filters": {
            "sortType": sort_type
        }
    }
    
    if repo_guid:
        data["filters"]["repoGuid"] = repo_guid.split(",") if "," in repo_guid else [repo_guid]
    if doc_type:
        data["filters"]["docType"] = doc_type.split(",") if "," in doc_type else [doc_type]
    
    try:
        response = requests.post(
            KU_SEARCH_URL,
            headers=headers,
            data=json.dumps(data, ensure_ascii=False),
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"code": 500, "message": str(e), "data": None}


def main():
    """主函数，解析命令行参数并执行搜索。"""
    parser = argparse.ArgumentParser(description="知识库搜索命令行工具")
    parser.add_argument("--word", required=True, help="查询词")
    parser.add_argument("--page", type=int, default=1, help="页码，默认 1")
    parser.add_argument("--page-size", type=int, default=10, help="每页大小，默认 10")
    parser.add_argument("--repo-guid", help="指定知识库搜索")
    parser.add_argument("--doc-type", help="文档类型")
    parser.add_argument("--sort-type", default="reme", help="排序方式：hot/reme",)
    parser.add_argument("--click-nl-query", action="store_true", help="使用自然语言查询（支持自然语言描述搜索意图）")
    
    args = parser.parse_args()
    
    result = search_ku(
        word=args.word,
        page_no=args.page,
        page_size=args.page_size,
        repo_guid=args.repo_guid,
        doc_type=args.doc_type,
        sort_type=args.sort_type,
        is_click_nl_query=args.click_nl_query
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
