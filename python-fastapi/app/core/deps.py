"""依赖注入"""

from typing import Generator
from app.db.session import SessionLocal


def get_db() -> Generator:
    """_summary_

    Yields:
        Generator: _description_
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
