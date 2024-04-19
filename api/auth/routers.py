import os

import aiofiles
from fastapi import UploadFile, Depends, HTTPException, Request, File
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession


from database import db_session
from api.auth.utils import password, token
from api.auth.models import UserModel
from api.auth.schemas import UserCreateSchema, UserLoginSchema

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post('/register', summary="Create new user")
async def create_user(schema: UserCreateSchema,
                      session: AsyncSession = Depends(db_session.get_async_session)):
    schema = schema.model_dump()
    if password.check(schema["password"]):
        pass
    query = select(UserModel.id_u).where(UserModel.email == schema["email"])
    result = await session.execute(query)
    if result.scalars().all():
        raise HTTPException(status_code=400, detail="Пользователь уже существует.")
    try:
        stmt = insert(UserModel).values(
            first_name=schema['first_name'],
            last_name=schema['last_name'],
            father_name=schema['father_name'],
            email=schema['email'],
            role=schema['role'],
            about=schema['about'],
            photo="media/user_photo/default.png",
            hashed_password=password.hash(schema["password"]))
        await session.execute(statement=stmt)
        await session.commit()
    except Exception:
        raise HTTPException(status_code=400, detail="Произошла неизвестная ошибка.")
    return JSONResponse(status_code=200, content={"detail": "Пользователь был добавлен."})


@router.post('/login', summary="Create access and refresh tokens")
async def login(schema: UserLoginSchema,
                session: AsyncSession = Depends(db_session.get_async_session)):
    schema = schema.model_dump()
    query = select(UserModel.hashed_password).where(UserModel.email == schema["email"])
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
    result = await session.execute(select(UserModel.id_u).where(UserModel.email == schema["email"]))
    user_id = result.scalars().all()[0]
    return JSONResponse(status_code=201, content={
        "access_token": token.create(user_id, type_="access"),
        "refresh_token": token.create(user_id, type_="refresh")
    })


@router.get('/refresh', summary="Update access and refresh tokens")
async def get_new_tokens(payload: dict = Depends(token.check),
                         session: AsyncSession = Depends(db_session.get_async_session)):
    query = select(UserModel.id_u).where(UserModel.id_u == int(payload["sub"]))
    result = await session.execute(query)
    result = result.all()
    if not result:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return JSONResponse(status_code=200, content={
        "access_token": token.create(payload["sub"], type_="access"),
        "refresh_token": token.create(payload["sub"], type_="refresh")
    })


@router.get('/logout', summary="Logout", dependencies=[Depends(token.check)])
async def logout():
    return JSONResponse(status_code=200, content={"detail": "Успешно."})


@router.get('/user', summary="Get information about user")
async def get_user(payload: dict = Depends(token.check),
                   session: AsyncSession = Depends(db_session.get_async_session)):
    query = select(
        UserModel.first_name,
        UserModel.last_name,
        UserModel.father_name,
        UserModel.email,
        UserModel.role,
        UserModel.about,
        UserModel.photo).where(
        UserModel.id_u == int(payload["sub"]))
    result = await session.execute(query)
    try:
        result = result.fetchone()
    except IndexError:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")
    return JSONResponse(status_code=200, content={"first_name": result[0],
                                                  "last_name": result[1],
                                                  "father_name": result[2],
                                                  "email": result[3],
                                                  "role": result[4],
                                                  "about": result[5],
                                                  "photo": result[6]})


@router.delete('/user', summary="Delete user")
async def delete_user(payload: dict = Depends(token.check),
                      session: AsyncSession = Depends(db_session.get_async_session)):
    query = select(UserModel.photo).where(UserModel.id_u == int(payload["sub"]))
    result = await session.execute(query)
    result = result.scalars().all()
    os.remove(result[0])

    stmt = delete(UserModel).where(UserModel.id_u == int(payload["sub"]))
    await session.execute(stmt)
    await session.commit()

    return JSONResponse(status_code=200, content={"detail": "Успешно."})


@router.patch('/user', summary="Change user's information")
async def patch_user(request: Request, payload: dict = Depends(token.check),
                     session: AsyncSession = Depends(db_session.get_async_session)):
    data = await request.json()
    stmt = update(UserModel).where(UserModel.id_u == int(payload["sub"])).values(name=data["name"])
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(status_code=200, content={"detail": "Успешно."})


@router.patch('/photo', summary="Update user's photo")
async def patch_photo(payload: dict = Depends(token.check), photo: UploadFile = File(...),
                      session: AsyncSession = Depends(db_session.get_async_session)):
    id_ = int(payload["sub"])
    query = select(UserModel.photo).where(UserModel.id_u == id_)
    result = await session.execute(query)
    result = result.scalars().all()
    if result[0] != photo.filename and result[0] != "media/user_photo/default.png":
        os.remove(result[0])
    try:
        file_path = f'media/user_photo/{photo.filename}'
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = photo.file.read()
            await out_file.write(content)
        stmt = update(UserModel).where(UserModel.id_u == id_).values(photo=file_path)
        await session.execute(statement=stmt)
        await session.commit()
    except Exception:
        raise HTTPException(status_code=400, detail="Произошла неизвестная ошибка.")

    return JSONResponse(status_code=200, content={"detail": "Успешно."})


@router.delete('/photo', summary="Delete user's photo")
async def delete_photo(payload: dict = Depends(token.check),
                       session: AsyncSession = Depends(db_session.get_async_session)):
    try:
        id_ = int(payload["sub"])
        query = select(UserModel.photo).where(UserModel.id_u == id_)
        result = await session.execute(query)
        result = result.scalars().all()
        os.remove(result[0])
        stmt = update(UserModel).where(UserModel.id_u == id_).values(photo="media/user_photo/default.png")
        await session.execute(statement=stmt)
        await session.commit()
    except Exception:
        raise HTTPException(status_code=400, detail="Произошла неизвестная ошибка.")

    return JSONResponse(status_code=200, content={"detail": "Успешно."})

# @router.get('/all_user', summary="Get all users")
# async def all_user(value: str, value2: str,session: AsyncSession = Depends(db.get_async_session)):
#     await session.execute(text(f'INSERT INTO "user"(name, hashed_password) VALUES ("{value}", "{value2}")'))
#     await session.commit()
#     return JSONResponse(status_code=200, content={"detail": "Успешно."})
