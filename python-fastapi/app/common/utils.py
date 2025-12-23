from uuid import UUID


def isUUID(value: str) -> bool:
    """判断是否为UUID"""
    try:
        UUID(value)
        return True
    except ValueError:
        return False
