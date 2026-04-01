from enum import Enum
from typing import Optional, Iterable, Sequence, Type, List
from sqlalchemy.orm import Query, DeclarativeBase
from sqlalchemy.sql.elements import ColumnElement
class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"

def parse_sort_string(raw:Optional[str], * , default: Optional[str] = None) -> list[tuple[str, SortDirection]]:
    """解析排序字符串（支持方式：1.fieldA:asc,fieldB:desc 2.fieldA,fieldB 3.fieldA:-fieldB）"""
    if not raw or not raw.strip():
        return []
    parts = [p.strip() for p in raw.split(',') if p.strip()]
    out: list[tuple[str, SortDirection]] = []
    for p in parts:
        if ":" in p:
            field, direction = p.split(':', 1)
            field = field.strip()
            direction = direction.strip().lower()
            if direction not in [SortDirection.ASC.value, SortDirection.DESC.value]:
                raise ValueError(f"Invalid sort direction: {direction}")
            out.append((field, SortDirection(direction)))
        elif p.startswith('-'):
            out.append((p[1:], SortDirection.DESC))
        else:
            out.append((p[1:].strip() if p.startswith('+') else p, SortDirection.ASC))    
    return out

def apply_sort_by(
    query: Query,
    model: Type[DeclarativeBase],
    *,
    sort_spec: Iterable[tuple[str, SortDirection]],
    allowed_fields: Optional[Iterable[str]] = None,
    default_order: Optional[Sequence[ColumnElement]] = None,
) -> Query:
    """应用排序到查询"""
    clauses:List[ColumnElement] = []
    for field_name, direction in sort_spec:
        if allowed_fields is not None and field_name not in allowed_fields:
            raise ValueError(f"Invalid sort field: {field_name}")
        if not hasattr(model, field_name):
            raise ValueError(f"Model {model.__name__} has no field {field_name}")
        col = getattr(model, field_name)
        clauses.append(col.desc() if direction == SortDirection.DESC else col.asc())
    if not clauses and default_order is not None:
        return query.order_by(*default_order)
    if not clauses:
        return query    
    return query.order_by(*clauses)


