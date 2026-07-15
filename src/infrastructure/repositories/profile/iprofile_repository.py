from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.models.profile.profile import Profile
from src.infrastructure.repositories.base.ibase_repository import IBaseRepository


class IProfileRepository(IBaseRepository, ABC):

    @abstractmethod
    async def insert_async(self, entity: Profile) -> Profile:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id_async(self, id: str) -> Optional[Profile]:
        raise NotImplementedError

    @abstractmethod
    async def get_all_async(self) -> List[Profile]:
        raise NotImplementedError

    @abstractmethod
    async def update_async(self, entity: Profile) -> Profile:
        raise NotImplementedError

    @abstractmethod
    async def delete_async(self, id: str) -> bool:
        raise NotImplementedError
