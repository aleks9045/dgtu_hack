import os

import aiofiles
from fastapi import UploadFile, Depends, HTTPException, Request, File
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from api.experts.schemas import ExpertLoginSchema, ExpertCreateSchema
from api.experts.models import ExpertModel
from database import db_session
from api.auth.utils import password, token
from api.admin.schemas import AdminLoginSchema
from api.admin.models import AdminModel

router = APIRouter(
    prefix="/experts",
    tags=["Experts"]
)


@router.post('/register', summary="Create new user")
async def create_user(schema: ExpertCreateSchema, payload: dict = Depends(token.check),
                      session: AsyncSession = Depends(db_session.get_async_session)):
    schema = schema.model_dump()
    if password.check(schema["password"]):
        pass
    query = select(ExpertModel.id_e).where(ExpertModel.email == schema["email"])
    result = await session.execute(query)
    if result.scalars().all():
        raise HTTPException(status_code=400, detail="Пользователь уже существует.")
    try:
        stmt = insert(ExpertModel).values(
            first_name=schema['first_name'],
            last_name=schema['last_name'],
            father_name=schema['father_name'],
            email=schema['email'],
            role=schema['role'],
            company=schema['company'],
            photo="media/user_photo/default.png",
            hashed_password=password.hash(schema["password"]))
        await session.execute(statement=stmt)
        await session.commit()
    except Exception:
        raise HTTPException(status_code=400, detail="Произошла неизвестная ошибка.")
    return JSONResponse(status_code=201, content={"detail": "Пользователь был добавлен."})


@router.post('/login', summary="Create access and refresh tokens for experts")
async def login(schema: ExpertLoginSchema,
                session: AsyncSession = Depends(db_session.get_async_session)):
    schema = schema.model_dump()
    query = select(ExpertModel.hashed_password).where(ExpertModel.email == schema["email"])
    result = await session.execute(query)
    result = result.scalars().all()
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Неверно введена почта или пароль."
        )
    hashed_pass = result[0]
    if not password.verify(schema["password"], hashed_pass):
        raise HTTPException(
            status_code=400,
            detail="Неверно введена почта или пароль."
        )
    result = await session.execute(select(ExpertModel.id_e).where(ExpertModel.email == schema["email"]))
    user_id = result.scalars().all()[0]
    return JSONResponse(status_code=201, content={
        "access_token": token.create(user_id, type_="access"),
        "refresh_token": token.create(user_id, type_="refresh")
    })

@router.get('/expert', summary="Get information about user")
async def get_user(payload: dict = Depends(token.check),
                   session: AsyncSession = Depends(db_session.get_async_session)):
    query = select(
        ExpertModel.id_e,
        ExpertModel.first_name,
        ExpertModel.last_name,
        ExpertModel.father_name,
        ExpertModel.email,
        ExpertModel.role,
        ExpertModel.company,
        ExpertModel.photo).where(
        ExpertModel.id_e == int(payload["sub"]))
    result = await session.execute(query)
    try:
        result = result.fetchone()
        print(result[0])
    except Exception:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")
    return JSONResponse(status_code=200, content={"id": result[0],
                                                  "first_name": result[1],
                                                  "last_name": result[2],
                                                  "father_name": result[3],
                                                  "email": result[4],
                                                  "role": result[5],
                                                  "about": result[6],
                                                  "photo": result[7]})