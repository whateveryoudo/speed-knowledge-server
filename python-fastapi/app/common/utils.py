from uuid import UUID
from typing import Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

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

def is_duplicate_entry(exc: IntegrityError) -> bool:
    orig = getattr(exc, 'orig', None)
    if orig is None:
        return False
    return orig.args[0] == 1062

def is_duplicate_on(exc: IntegrityError, *names: str) -> bool:
    if not is_duplicate_entry(exc):
        return False
    msg = str(getattr(exc, 'orig', ''))
    return any(name in msg for name in names)
def is_slug_duplicate(exc: IntegrityError, check_unique_key: str) -> bool:
    return is_duplicate_on(exc, check_unique_key)

def next_order_index(db: Session, model, **filters) -> int:
    """获取下一个排序索引"""
    max_index = db.query(func.max(model.order_index)).filter_by(**filters).scalar()
    return (max_index or -1) + 1
