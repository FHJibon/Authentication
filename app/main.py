from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import traceback
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.model.model import Base
from app.api.v1.endpoints.auth import router as auth_router

app = FastAPI(title="FastAPI Authentication")

@app.on_event("startup")
async def startup():
    from app.utils.db import engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    return JSONResponse(status_code=500, content={
        "error": "Internal Server Error",
        "detail": str(exc),
        "path": request.url.path,
        "trace": tb
    })


from app.utils.db import get_db
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "FastAPI Auth is running!"}