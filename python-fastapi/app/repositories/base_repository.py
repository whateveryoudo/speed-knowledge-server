from typing import Generic, Type, TypeVar
from app.core.mixins import SoftDeleteMixin
from sqlalchemy.orm import Query, Session

ModelType = TypeVar("ModelType")
SoftDeleteModelType = TypeVar("SoftDeleteModelType", bound=SoftDeleteMixin)


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model

    def all_query(self) -> Query:
        return self.db.query(self.model)
        
    def add(self, entity: ModelType) -> ModelType:
        self.db.add(entity)
        return entity

    def delete(self, entity: ModelType) -> None:
        self.db.delete(entity)

    def flush(self) -> None:
        self.db.flush()

    def refresh(self, entity: ModelType) -> ModelType:
        self.db.refresh(entity)
        return entity


class SoftDeleteRepository(BaseRepository[SoftDeleteModelType]):
    def __init__(self, db: Session, model: Type[SoftDeleteModelType]):
        super().__init__(db, model)

    def active_query(self) -> Query:
        return self.model.filter_active(self.all_query())

    def deleted_query(self) -> Query:
        return self.model.filter_deleted(self.all_query())
