from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.models.profile.profile import Profile


class IProfileService(ABC):

    @abstractmethod
    async def create_async(self, first_name: str, last_name: str) -> Profile:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id_async(self, profile_id: str) -> Optional[Profile]:
        raise NotImplementedError

    @abstractmethod
    async def get_all_async(self) -> List[Profile]:
        raise NotImplementedError

    @abstractmethod
    async def update_async(
        self, profile_id: str, first_name: str, last_name: str
    ) -> Optional[Profile]:
        raise NotImplementedError

    @abstractmethod
    async def delete_async(self, profile_id: str) -> bool:
        raise NotImplementedError
