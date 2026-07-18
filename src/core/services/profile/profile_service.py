from typing import List, Optional

from src.infrastructure.di.inject import inject
from src.infrastructure.models.profile import Profile
from src.infrastructure.repositories.profile.profile_repository import ProfileRepository


@inject
class ProfileService:

    def __init__(self, profile_repository: ProfileRepository):
        self._profile_repository = profile_repository

    async def create_async(self, first_name: str, last_name: str) -> Profile:
        profile = Profile(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
        )
        return await self._profile_repository.insert_async(profile)

    async def get_by_id_async(self, profile_id: str) -> Optional[Profile]:
        return await self._profile_repository.get_by_id_async(profile_id)

    async def get_all_async(self) -> List[Profile]:
        return await self._profile_repository.get_all_async()

    async def update_async(
        self, profile_id: str, first_name: str, last_name: str
    ) -> Optional[Profile]:
        profile = await self._profile_repository.get_by_id_async(profile_id)
        if profile is None:
            return None

        profile.first_name = first_name.strip()
        profile.last_name = last_name.strip()
        return await self._profile_repository.update_async(profile)

    async def delete_async(self, profile_id: str) -> bool:
        return await self._profile_repository.delete_async(profile_id)
