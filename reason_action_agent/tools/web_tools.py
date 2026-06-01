"""网络工具 - 搜索和天气"""

from urllib.parse import quote

import requests

from reason_action_agent.tools.registry import tool


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    搜索网页获取信息
    
    Args:
        query: 搜索关键词
        max_results: 最大返回结果数，默认 5
    
    Returns:
        搜索结果摘要
    """
    # 使用 DuckDuckGo Instant Answer API（无需 API Key）
    url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1"
    
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ReActAgent/1.0)"},
        )
        response.raise_for_status()
        data = response.json()
        
        results = []
        
        # 提取摘要
        if abstract := data.get("Abstract"):
            results.append(f"摘要: {abstract}")
        
        # 提取相关主题
        for topic in data.get("RelatedTopics", [])[:max_results]:
            if isinstance(topic, dict) and "Text" in topic:
                results.append(f"- {topic['Text']}")
        
        if not results:
            return f"未找到关于 '{query}' 的相关信息，建议使用浏览器搜索"
        
        return "\n".join(results)
    
    except requests.RequestException as e:
        return f"搜索失败（网络错误）: {e}\n建议使用浏览器搜索: https://duckduckgo.com/?q={quote(query)}"


@tool
def get_weather(city: str) -> str:
    """
    获取城市天气信息
    
    使用场景：
    - 查询天气：get_weather("北京")
    - 多个城市：分别调用多次
    
    参数说明：
    - city: 城市名称（必须），如 "北京", "上海", "广州"
    
    返回：格式化的天气信息（温度、湿度、风速等）
    
    示例：
    - get_weather("北京")
    - get_weather(city="上海")
    """
    # 使用 wttr.in（免费天气服务，无需 API Key）
    url = f"https://wttr.in/{quote(city)}?format=j1&lang=zh"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 提取当前天气
        current = data.get("current_condition", [{}])[0]
        weather_desc = current.get("lang_zh", [{}])[0].get("value", current.get("weatherDesc", [{}])[0].get("value", "未知"))
        temp = current.get("temp_C", "未知")
        feels_like = current.get("FeelsLikeC", "未知")
        humidity = current.get("humidity", "未知")
        wind = current.get("windspeedKmph", "未知")
        
        # 提取今日预报
        today = data.get("weather", [{}])[0]
        max_temp = today.get("maxtempC", "未知")
        min_temp = today.get("mintempC", "未知")
        
        return f"""🏙️ {city} 天气
━━━━━━━━━━━━━━━━━━
🌡️ 当前温度: {temp}°C (体感 {feels_like}°C)
🌤️ 天气: {weather_desc}
💧 湿度: {humidity}%
💨 风速: {wind} km/h
📈 今日: {min_temp}°C ~ {max_temp}°C
━━━━━━━━━━━━━━━━━━"""
    
    except requests.RequestException as e:
        return f"获取天气失败: {e}"


@tool
def fetch_url(url: str, timeout: int = 10) -> str:
    """
    抓取网页内容
    
    Args:
        url: 网页 URL
        timeout: 超时秒数，默认 10
    
    Returns:
        网页内容（纯文本）
    """
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ReActAgent/1.0)"},
        )
        response.raise_for_status()
        
        # 简单提取文本（去除 HTML 标签）
        import re
        text = re.sub(r"<[^>]+>", " ", response.text)
        text = re.sub(r"\s+", " ", text).strip()
        
        # 限制长度
        max_chars = 5000
        if len(text) > max_chars:
            text = text[:max_chars] + "...(已截断)"
        
        return text
    
    except requests.RequestException as e:
        return f"抓取网页失败: {e}"
