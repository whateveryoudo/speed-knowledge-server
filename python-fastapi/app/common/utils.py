from uuid import UUID
from typing import Any


def isUUID(value: str) -> bool:
    """判断是否为UUID"""
    try:
        UUID(value)
        return True
    except ValueError:
        return False


def get_field(x: Any, key: str, default: Any = None) -> Any:
    """获取字典或对象的属性值"""
    if isinstance(x, dict):
        return x.get(key, default)
    elif isinstance(x, object):
        if hasattr(x, key):
            return getattr(x, key)
        return default
    else:
        raise ValueError(f"x must be a dict or object, but got {type(x)}")
