from fastapi import APIRouter, status
from datetime import datetime
from typing import Dict

from .dtos.health_check_dto import HealthCheckResponse 


class HealthCheckController:

    def __init__(self):
        super(HealthCheckController, self).__init__()

    def api(self):
        router = APIRouter(
            prefix="",
            tags=["Health Check"],
            responses={404: {"description": "Not found"}},
        )

        @router.get(
            "/version",
            response_model=HealthCheckResponse,
            status_code=status.HTTP_200_OK,
            summary="Get Service Version",
            description="""
            Returns the current version of the service and the current date/time.
            This endpoint can be used for health checks and version verification.
            """,
            responses={
                200: {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "example": {
                                "message": "version: 1.3.10.45",
                                "date_time": "2024-04-05T12:00:00"
                            }
                        }
                    }
                }
            }
        )
        async def health_check() -> Dict:
            return {
                "message": "version: 1.3.10.45",
                "date_time": datetime.now()
            }
    
        return router
