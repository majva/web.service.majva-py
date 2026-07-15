from functools import wraps
from fastapi import HTTPException

def http_exception_handler(message: str, status_code: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                raise HTTPException(status_code=status_code, detail=f"{message}")
        return wrapper
    return decorator