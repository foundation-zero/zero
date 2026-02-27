from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy import text

from loads.api.db import SessionManager
from loads.api.dependencies import get_sessionmanager

router = APIRouter(tags=["health"])


@router.get("/live")
async def live():
    return {"status": "alive"}


@router.get("/ready")
async def ready(
    sessionmanager: Annotated[SessionManager, Depends(get_sessionmanager)],
    response: Response,
):
    try:
        async with sessionmanager.session() as session:
            await session.execute(text("SELECT 1"))
        # Messaging readiness could be included here
        # For now, we're relying on the finish in the lifespan to kill the app
        response.status_code = 200
        return {"status": "ready"}
    except Exception as e:
        response.status_code = 500
        return {"status": "not ready", "error": str(e)}
