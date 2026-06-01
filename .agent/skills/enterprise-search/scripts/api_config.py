#!/usr/bin/env python3
"""
API 端点配置模块 - 企业搜索所有脚本共享。

集中管理所有 API 端点，便于统一维护和迁移。
"""

# API 基础路径
BASE_URL = "https://apigo.baidu-int.com/search-open/openapi/search-auth/openapi"

# 搜索 API 端点
ENDPOINTS = {
    # 搜索接口
    "neisou_search": f"{BASE_URL}/search/neisou",
    "meeting_search": f"{BASE_URL}/search/meeting",
    "weekly_report_search": f"{BASE_URL}/search/weeklyReport",
    "ku_search": f"{BASE_URL}/search/kuweb",
    "okr_search": f"{BASE_URL}/search/okr",
    
    # 详情获取接口
    "neisou_fetch": f"{BASE_URL}/fetch/solr",
    "weekly_report_fetch": f"{BASE_URL}/fetch/weeklyReport",
    "okr_fetch": f"{BASE_URL}/fetch/okr",

    # 通讯录搜索接口
    "address_search": f"{BASE_URL}/search/query",
}


def get_endpoint(name: str) -> str:
    """获取指定 API 端点 URL
    
    Args:
        name: 端点名称，如 "neisou_search"
    
    Returns:
        API URL 字符串
        
    Raises:
        KeyError: 端点名称不存在
    """
    if name not in ENDPOINTS:
        raise KeyError(f"未知的 API 端点: {name}，可用端点: {list(ENDPOINTS.keys())}")
    return ENDPOINTS[name]


# 导出常用端点
NEISOU_SEARCH_URL = ENDPOINTS["neisou_search"]
NEISOU_FETCH_URL = ENDPOINTS["neisou_fetch"]
MEETING_SEARCH_URL = ENDPOINTS["meeting_search"]
WEEKLY_REPORT_SEARCH_URL = ENDPOINTS["weekly_report_search"]
WEEKLY_REPORT_FETCH_URL = ENDPOINTS["weekly_report_fetch"]
KU_SEARCH_URL = ENDPOINTS["ku_search"]
OKR_SEARCH_URL = ENDPOINTS["okr_search"]
OKR_FETCH_URL = ENDPOINTS["okr_fetch"]
ADDRESS_SEARCH_URL = ENDPOINTS["address_search"]
