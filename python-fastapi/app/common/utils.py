from uuid import UUID
from typing import Any
import re
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


_IPV4_HOST_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def get_space_subdomain(host: str) -> str | None:
    """从 Host 解析空间子域名；localhost / IP / 裸域名 返回 None"""
    hostname = host.split(";")[0].split(":")[0].lower()
    if not hostname or hostname in {"localhost", "127.0.0.1"}:
        return None
    if _IPV4_HOST_RE.match(hostname):
        return None
    parts = hostname.split(".")
    if len(parts) >= 3 and parts[0] not in {"localhost", "www"}:
        return parts[0]
    return None


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
    orig = getattr(exc, "orig", None)
    if orig is None:
        return False
    return orig.args[0] == 1062


def is_duplicate_on(exc: IntegrityError, *names: str) -> bool:
    if not is_duplicate_entry(exc):
        return False
    msg = str(getattr(exc, "orig", ""))
    return any(name in msg for name in names)


def is_slug_duplicate(exc: IntegrityError, check_unique_key: str) -> bool:
    return is_duplicate_on(exc, check_unique_key)


def next_order_index(db: Session, model, **filters) -> int:
    """获取下一个排序索引"""
    max_index = db.query(func.max(model.order_index)).filter_by(**filters).scalar()
    return (max_index or -1) + 1


def prepare_insert_order_index(
    db: Session, model, target_index: int, **filters
) -> dict:
    """准备插入排序索引"""
    db.query(model).filter_by(**filters).filter(
        model.order_index >= target_index
    ).update({model.order_index: model.order_index + 1}, synchronize_session=False)
    return target_index
