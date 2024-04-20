import aiofiles
from aiofiles import os
from fastapi import Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.utils import password, token
from api.experts.models import ExpertModel, CompanyModel, CaseModel
from api.experts.schemas import ExpertLoginSchema, ExpertCreateSchema, AddCaseSchema, AddCaseFileSchema
from database import db_session

router = APIRouter(
    prefix="/experts",
    tags=["Experts"]
)


@router.post('/register', summary="Create new expert")
async def create_expert(schema: ExpertCreateSchema, payload: dict = Depends(token.check),
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
    return JSONResponse(status_code=201, content={
        "access_token": token.create(schema["email"], type_="access"),
        "refresh_token": token.create(schema["email"], type_="refresh")
    })


@router.get('/expert', summary="Get information about expert")
async def get_expert(payload: dict = Depends(token.check),
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
        ExpertModel.email == payload["sub"])
    result = await session.execute(query)
    try:
        result = result.fetchone()
        r = result[0]
    except Exception:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")
    return JSONResponse(status_code=200, content={"id": result[0],
                                                  "first_name": result[1],
                                                  "last_name": result[2],
                                                  "father_name": result[3],
                                                  "email": result[4],
                                                  "role": result[5],
                                                  "company": result[6],
                                                  "photo": result[7]})

@router.patch('/photo', summary="Change expert's photo")
async def patch_photo(payload: dict = Depends(token.check), photo: UploadFile = File(...),
                      session: AsyncSession = Depends(db_session.get_async_session)):
    query = select(ExpertModel.photo).where(ExpertModel.email == payload["sub"])
    result = await session.execute(query)
    result = result.scalars().all()
    if result[0] != photo.filename and result[0] != "media/user_photo/default.png":
        await os.remove(result[0])
    try:
        file_path = f'media/user_photo/{photo.filename}'
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = photo.file.read()
            await out_file.write(content)
        stmt = update(ExpertModel).where(ExpertModel.email == payload["sub"]).values(photo=file_path)
        await session.execute(statement=stmt)
        await session.commit()
    except Exception:
        raise HTTPException(status_code=400, detail="Произошла неизвестная ошибка.")
    return JSONResponse(status_code=200, content={"detail": "Успешно."})

@router.delete('/photo', summary="Delete expert's photo")
async def delete_photo(payload: dict = Depends(token.check),
                       session: AsyncSession = Depends(db_session.get_async_session)):
    try:
        query = select(ExpertModel.photo).where(ExpertModel.email == payload["sub"])
        result = await session.execute(query)
        result = result.scalars().all()
        await os.remove(result[0])
        stmt = update(ExpertModel).where(ExpertModel.email == payload["sub"]).values(photo="media/user_photo/default.png")
        await session.execute(statement=stmt)
        await session.commit()
    except Exception:
        raise HTTPException(status_code=400, detail="Произошла неизвестная ошибка.")
    return JSONResponse(status_code=200, content={"detail": "Успешно."})

@router.get('/company', summary="Get information about company")
async def get_company(id_co: int,
                      session: AsyncSession = Depends(db_session.get_async_session)):
    result = await session.execute(
        select(CompanyModel.name).where(CompanyModel.id_co == id_co))
    result = result.fetchone()
    return JSONResponse(status_code=200, content={"name": result[0]})


@router.post('/case', summary="Add case")
async def add_case(schema: AddCaseSchema, payload: dict = Depends(token.check),
                   session: AsyncSession = Depends(db_session.get_async_session)):
    print(schema)
    print(schema)
    print(schema)
    stmt = insert(CaseModel).values(
        name=schema["name"],
        about=schema["about"],
        company=schema["id_co"])
    await session.execute(statement=stmt)
    await session.commit()
    print("OKKEEEEEE")
    return JSONResponse(status_code=200, content={"detail": "Кейс успешно добавлен."})


@router.delete("/case")
async def delete_case(id_ca: int, payload: dict = Depends(token.check),
                      session: AsyncSession = Depends(db_session.get_async_session)):
    await session.execute(delete(CaseModel).where(CaseModel.id_ca == id_ca))
    await session.commit()
    return JSONResponse(status_code=200, content={"detail": "Успешно."})

@router.patch('/file', summary="Change case's file")
async def patch_file(schema: AddCaseFileSchema, payload: dict = Depends(token.check), photo: UploadFile = File(...),
                      session: AsyncSession = Depends(db_session.get_async_session)):
    result = await session.execute(select(CaseModel.file).where(CaseModel.id_ca == schema["id_ca"]))
    result = result.scalars().all()
    if result[0] != photo.filename and result[0] != "media/case_files/default.png":
        await os.remove(result[0])
    try:
        file_path = f'media/case_files/{photo.filename}'
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = photo.file.read()
            await out_file.write(content)
        stmt = update(CaseModel).where(CaseModel.id_ca == schema["id_ca"]).values(file=file_path)
        await session.execute(statement=stmt)
        await session.commit()
    except Exception:
        raise HTTPException(status_code=400, detail="Произошла неизвестная ошибка.")
    return JSONResponse(status_code=200, content={"detail": "Успешно."})

@router.delete('/file', summary="Delete case's file")
async def delete_file(payload: dict = Depends(token.check),
                       session: AsyncSession = Depends(db_session.get_async_session)):
    try:
        query = select(ExpertModel.photo).where(ExpertModel.email == payload["sub"])
        result = await session.execute(query)
        result = result.scalars().all()
        await os.remove(result[0])
        stmt = update(ExpertModel).where(ExpertModel.email == payload["sub"]).values(photo="media/user_photo/default.png")
        await session.execute(statement=stmt)
        await session.commit()
    except Exception:
        raise HTTPException(status_code=400, detail="Произошла неизвестная ошибка.")
    return JSONResponse(status_code=200, content={"detail": "Успешно."})

@router.get('/all_case', summary="Get all cases")
async def all_case(session: AsyncSession = Depends(db_session.get_async_session)):
    res_dict = []
    result = await session.execute(
        select(CaseModel.id_ca, CaseModel.name, CaseModel.about, CaseModel.file, CaseModel.company).where(1 == 1))
    for i in result.all():
        result = await session.execute(select(CompanyModel.name).where(CompanyModel.id_co == i[0]))
        company_name = result.fetchone()[0]
        res_dict.append({"id_ca": i[0],
                         "name": i[1],
                         "about": i[2],
                         "file": i[3],
                         "company": company_name})
    return JSONResponse(status_code=200, content=res_dict)
