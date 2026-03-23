from langchain.tools import tool


@tool
def web_search(query: str) -> str:
    """天气查询"""
    return "今天成都天气晴朗，温度20度，空气质量良好。"
