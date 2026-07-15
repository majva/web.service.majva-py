from typing import List, Optional

from src.domain.models.profile.profile import Profile
from src.infrastructure.context.sql_db.psql_dbcontext import PsqlDbContext
from src.infrastructure.di import inject
from src.infrastructure.repositories.base.base_repository import BaseRepository
from src.infrastructure.repositories.profile.iprofile_repository import IProfileRepository


@inject
class ProfileRepository(BaseRepository[Profile], IProfileRepository):

    def __init__(self, db_context: PsqlDbContext):
        super().__init__(db_context=db_context, model=Profile)

    async def insert_async(self, entity: Profile) -> Profile:
        return await super().insert_async(entity)

    async def get_by_id_async(self, id: str) -> Optional[Profile]:
        return await super().get_by_id_async(id)

    async def get_all_async(self) -> List[Profile]:
        return await super().get_all_async()

    async def update_async(self, entity: Profile) -> Profile:
        return await super().update_async(entity)

    async def delete_async(self, id: str) -> bool:
        return await super().delete_async(id)
