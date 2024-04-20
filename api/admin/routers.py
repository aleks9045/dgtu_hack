import os

import aiofiles
from fastapi import UploadFile, Depends, HTTPException, Request, File
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from database import db_session
from api.auth.utils import password, token
from api.admin.schemas import AdminLoginSchema
from api.admin.models import AdminModel

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.post('/login', summary="Create access and refresh tokens for admin")
async def login(schema: AdminLoginSchema,
                session: AsyncSession = Depends(db_session.get_async_session)):
    schema = schema.model_dump()
    result = await session.execute(select(AdminModel.hashed_password).where(AdminModel.name == schema["name"]))
    result = result.scalars().all()
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Неверно введены данные."
        )
    hashed_pass = result[0]
    if not password.verify(schema["password"], hashed_pass):
        raise HTTPException(
            status_code=400,
            detail="Неверно введены данные."
        )
    result = await session.execute(select(AdminModel.id_a).where(AdminModel.name == schema["name"]))
    user_id = result.scalars().all()[0]
    return JSONResponse(status_code=201, content={
        "access_token": token.create(user_id, type_="access"),
        "refresh_token": token.create(user_id, type_="refresh")
    })