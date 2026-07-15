
from pydantic import BaseModel


class UserAuth(BaseModel):
    id: str
    username: str
    roles: list
