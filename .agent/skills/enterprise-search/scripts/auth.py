#!/usr/bin/env python3
"""
统一认证模块 - 企业搜索所有脚本共享。

仅从本地缓存文件读取 ugate token；缺失时退出码 2，由 Agent 调用 get-ugate-token skill 后再重试。

使用方式：
    from auth import get_auth_headers, get_auth_info
"""

import json
import os
import sys
from pathlib import Path
from functools import lru_cache
from typing import Optional


def _read_ugate_token_from_file(username: str) -> Optional[str]:
    """从 ~/.config/uuap/.eac_ugate_token_{username} 读取 token。"""
    cache_file = Path.home() / ".config" / "uuap" / f".eac_ugate_token_{username}"
    if not cache_file.is_file():
        return None
    try:
        raw = cache_file.read_text(encoding="utf-8").strip()
        if not raw:
            return None
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return raw
        if isinstance(data, dict):
            t = data.get("token")
            if t:
                return str(t)
        return None
    except OSError:
        return None


class AuthConfig:
    """认证配置管理"""

    @staticmethod
    @lru_cache(maxsize=1)
    def get_username() -> str:
        """获取当前用户名（带缓存）"""
        username = os.environ.get('SANDBOX_USERNAME') or os.environ.get('BAIDU_CC_USERNAME')
        if not username:
            print("错误: 未设置环境变量 SANDBOX_USERNAME 或 BAIDU_CC_USERNAME", file=sys.stderr)
            sys.exit(1)
        return username

    @staticmethod
    @lru_cache(maxsize=1)
    def get_ugate_token() -> str:
        """从本地缓存文件读取 ugate token（带缓存）。"""
        username = AuthConfig.get_username()
        token = _read_ugate_token_from_file(username)
        if not token:
            print(
                "错误: 未从本地读取到 ugate token（~/.config/uuap/.eac_ugate_token_*）。",
                file=sys.stderr,
            )
            print(
                "请先调用 get-ugate-token skill 完成授权或写入 token，再重试本操作。",
                file=sys.stderr,
            )
            sys.exit(2)
        return token

    @classmethod
    def get_auth_info(cls) -> tuple:
        """获取认证信息元组

        Returns:
            (username, ugate_token) 元组
        """
        return cls.get_username(), cls.get_ugate_token()

    @classmethod
    def get_auth_headers(cls) -> dict:
        """获取认证请求头（search 接口使用，header 为小写 ugate-token）"""
        return {
            "Content-Type": "application/json",
            "ugate-token": cls.get_ugate_token(),
            "uuap": cls.get_username()
        }

    @classmethod
    def get_fetch_headers(cls) -> dict:
        """获取认证请求头（fetch 接口使用，header 为大写 Ugate-Token）"""
        return {
            "Content-Type": "application/json",
            "Ugate-Token": cls.get_ugate_token(),
            "uuap": cls.get_username()
        }

    @classmethod
    def clear_cache(cls):
        """清除缓存（用于 token 刷新后重新获取）"""
        cls.get_username.cache_clear()
        cls.get_ugate_token.cache_clear()


# 便捷函数
def get_auth_headers() -> dict:
    """获取认证请求头 - search 接口"""
    return AuthConfig.get_auth_headers()


def get_fetch_headers() -> dict:
    """获取认证请求头 - fetch 接口"""
    return AuthConfig.get_fetch_headers()


def get_auth_info() -> tuple:
    """获取认证信息元组"""
    return AuthConfig.get_auth_info()


if __name__ == "__main__":
    print("测试认证模块...")
    try:
        username, token = get_auth_info()
        print(f"用户名: {username}")
        print(f"Token: {token[:20]}..." if len(token) > 20 else f"Token: {token}")
        print("认证模块工作正常！")
    except Exception as e:
        print(f"认证错误: {e}", file=sys.stderr)
        sys.exit(1)
