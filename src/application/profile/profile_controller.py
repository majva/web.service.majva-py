from typing import List

from fastapi import APIRouter, HTTPException, status

from src.application.profile.dtos.profile_dto import (
    CreateProfileDto,
    ProfileResponseDto,
    UpdateProfileDto,
)
from src.core.services.profile.profile_service import ProfileService
from src.infrastructure.di.inject import inject


@inject
class ProfileController:

    def __init__(self, profile_service: ProfileService):
        self._profile_service = profile_service

    def api(self):
        router = APIRouter(
            prefix="",
            tags=["Profile"],
            responses={404: {"description": "Not found"}},
        )

        @router.post(
            "/",
            response_model=ProfileResponseDto,
            status_code=status.HTTP_201_CREATED,
            summary="Create profile",
        )
        async def create_profile(payload: CreateProfileDto) -> ProfileResponseDto:
            profile = await self._profile_service.create_async(
                first_name=payload.first_name,
                last_name=payload.last_name,
            )
            return ProfileResponseDto.model_validate(profile)

        @router.get(
            "/",
            response_model=List[ProfileResponseDto],
            status_code=status.HTTP_200_OK,
            summary="List profiles",
        )
        async def list_profiles() -> List[ProfileResponseDto]:
            profiles = await self._profile_service.get_all_async()
            return [ProfileResponseDto.model_validate(p) for p in profiles]

        @router.get(
            "/{profile_id}",
            response_model=ProfileResponseDto,
            status_code=status.HTTP_200_OK,
            summary="Get profile by id",
        )
        async def get_profile(profile_id: str) -> ProfileResponseDto:
            profile = await self._profile_service.get_by_id_async(profile_id)
            if profile is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Profile '{profile_id}' not found",
                )
            return ProfileResponseDto.model_validate(profile)

        @router.put(
            "/{profile_id}",
            response_model=ProfileResponseDto,
            status_code=status.HTTP_200_OK,
            summary="Update profile",
        )
        async def update_profile(
            profile_id: str, payload: UpdateProfileDto
        ) -> ProfileResponseDto:
            profile = await self._profile_service.update_async(
                profile_id=profile_id,
                first_name=payload.first_name,
                last_name=payload.last_name,
            )
            if profile is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Profile '{profile_id}' not found",
                )
            return ProfileResponseDto.model_validate(profile)

        @router.delete(
            "/{profile_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete profile",
        )
        async def delete_profile(profile_id: str) -> None:
            deleted = await self._profile_service.delete_async(profile_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Profile '{profile_id}' not found",
                )

        return router
