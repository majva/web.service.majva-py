from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select

from src.infrastructure.context.sql_db.psql_dbcontext import PsqlDbContext
from src.infrastructure.repositories.base.ibase_repository import IBaseRepository

T = TypeVar("T")


class BaseRepository(IBaseRepository, Generic[T]):

    def __init__(self, db_context: PsqlDbContext, model: Type[T]):
        self._db_context = db_context
        self._model = model

    async def insert_async(self, entity: T) -> T:
        async with self._db_context.session() as session:
            session.add(entity)
            await session.commit()
            await session.refresh(entity)
            return entity

    async def insert_and_get_id_async(self, entity: T) -> Any:
        saved = await self.insert_async(entity)
        return getattr(saved, "id", None)

    async def get_by_id_async(self, id: Any) -> Optional[T]:
        async with self._db_context.session() as session:
            result = await session.execute(
                select(self._model).where(self._model.id == id)
            )
            return result.scalar_one_or_none()

    async def get_all_async(self) -> List[T]:
        async with self._db_context.session() as session:
            result = await session.execute(select(self._model))
            return list(result.scalars().all())

    async def update_async(self, entity: T) -> T:
        async with self._db_context.session() as session:
            merged = await session.merge(entity)
            await session.commit()
            await session.refresh(merged)
            return merged

    async def delete_async(self, id: Any) -> bool:
        async with self._db_context.session() as session:
            result = await session.execute(
                select(self._model).where(self._model.id == id)
            )
            entity = result.scalar_one_or_none()
            if entity is None:
                return False
            await session.delete(entity)
            await session.commit()
            return True
