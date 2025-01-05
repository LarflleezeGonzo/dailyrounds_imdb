from typing import Any

from fastapi import APIRouter

router = APIRouter(tags=["Ping"])


@router.get("/ping")
def ping() -> Any:
    """
    Health Check.
    """

    return "Service is up!"
