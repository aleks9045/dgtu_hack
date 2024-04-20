import aiofiles
from aiofiles import os
from fastapi import Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.models import UserModel
from api.auth.utils import token
from api.teams.models import TeamModel, TeamLeadModel, JobModel
from api.teams.schemas import TeamCreateSchema, TeamPatchSchema, AddJobSchema
from api.teams.tasks import send_notification_add, send_notification_delete
from api.teams.utils import user_exists
from database import db_session

router = APIRouter(
    prefix="/teams",
    tags=["Teams"]
)


@router.post("/team")
async def create_team(schema: TeamCreateSchema, payload: dict = Depends(token.check),
                      session: AsyncSession = Depends(db_session.get_async_session)):
    schema = schema.model_dump()
    stmt = insert(TeamModel).values(name=schema['name'], about=schema['about'], banner='media/teams_banner/default.png')
    await session.execute(stmt)
    await session.commit()
    result = await session.execute(select(TeamModel.id_t).where(TeamModel.name == schema["name"]))
    id_t = result.fetchone()[0]
    stmt = insert(TeamLeadModel).values(user=schema["id_u"], team=id_t)
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(status_code=200, content={"detail": "Команда была добавлена.",
                                                  "id_t": id_t})


@router.get("/team")
async def get_team_by_user(id_u: int, payload: dict = Depends(token.check),
                           session: AsyncSession = Depends(db_session.get_async_session)):
    await user_exists(session, id_u)
    result = await session.execute(select(UserModel.team).where(UserModel.id_u == id_u))
    team = result.fetchone()
    if team[0] is None:
        result = await session.execute(select(TeamLeadModel.team).where(TeamLeadModel.user == id_u))
        team = result.fetchone()
        if team is None:
            return JSONResponse(status_code=200, content={"detail": ""})

    result = await session.execute(
        select(TeamModel.id_t, TeamModel.name, TeamModel.about, TeamModel.banner).where(TeamModel.id_t == team[0]))
    team_user = result.fetchone()
    return JSONResponse(status_code=200, content={"id_t": team_user[0],
                                                  "name": team_user[1],
                                                  "about": team_user[2],
                                                  "banner": team_user[3]})


@router.patch("/team")
async def patch_team(schema: TeamPatchSchema, payload: dict = Depends(token.check),
                     session: AsyncSession = Depends(db_session.get_async_session)):
    schema = schema.model_dump()
    result = await session.execute(select(
        TeamModel.name, TeamModel.about).where(
        TeamModel.id_t == schema["id_t"]))
    result = result.fetchone()
    print(schema)
    for count, i in enumerate(schema.keys()):
        if schema[i] is None:
            schema[i] = result[count - 1]
    stmt = update(TeamModel).where(TeamModel.id_t == schema["id_t"]).values(
        name=schema['name'],
        about=schema['about']
    )
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(status_code=200, content={"detail": "Успешно."})


@router.patch('/banner', summary="Change team's banner")
async def patch_banner(id_t: int, payload: dict = Depends(token.check), photo: UploadFile = File(...),
                       session: AsyncSession = Depends(db_session.get_async_session)):
    result = await session.execute(select(TeamModel.banner).where(TeamModel.id_t == id_t))
    result = result.scalars().all()
    if result[0] != photo.filename and result[0] != "media/teams_banner/default.png":
        await os.remove(result[0])
    try:
        file_path = f'media/teams_banner/{photo.filename}'
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = photo.file.read()
            await out_file.write(content)
        stmt = update(TeamModel).where(TeamModel.id_t == id_t).values(banner=file_path)
        await session.execute(statement=stmt)
        await session.commit()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Произошла неизвестная ошибка.")

    return JSONResponse(status_code=200, content={"detail": "Успешно."})


@router.delete('/banner', summary="Delete teams's banner")
async def delete_banner(id_t: int, payload: dict = Depends(token.check),
                        session: AsyncSession = Depends(db_session.get_async_session)):
    try:
        query = select(TeamModel.banner).where(TeamModel.id_t == id_t)
        result = await session.execute(query)
        result = result.scalars().all()
        await os.remove(result[0])
        stmt = update(UserModel).where(UserModel.email == payload["sub"]).values(photo="media/teams_banner/default.png")
        await session.execute(statement=stmt)
        await session.commit()
    except Exception:
        raise HTTPException(status_code=400, detail="Произошла неизвестная ошибка.")

    return JSONResponse(status_code=200, content={"detail": "Успешно."})


@router.delete("/user")
async def delete_user_from_team(id_u: int, payload: dict = Depends(token.check),
                                session: AsyncSession = Depends(db_session.get_async_session)):
    stmt = update(UserModel).where(UserModel.id_u == id_u).values(team=None)
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(status_code=200, content={"detail": "Пользователь был успешно удалён."})


@router.get("/users")
async def get_all_users_from_team(id_t: int, payload: dict = Depends(token.check),
                                  session: AsyncSession = Depends(db_session.get_async_session)):
    res_dict = []
    result = await session.execute(
        select(UserModel.id_u, UserModel.first_name, UserModel.last_name, UserModel.father_name,
               UserModel.email, UserModel.role, UserModel.about, UserModel.photo).where(UserModel.team == id_t))
    for i in result.all():
        res_dict.append({"id": i[0],
                         "first_name": i[1],
                         "last_name": i[2],
                         "father_name": i[3],
                         "email": i[4],
                         "role": i[5],
                         "about": i[6],
                         "photo": i[7],
                         "type": "member"})
    result = await session.execute(select(TeamLeadModel.user).where(TeamLeadModel.team == id_t))
    teamlead_id = result.fetchone()[0]
    result = await session.execute(
        select(UserModel.id_u, UserModel.first_name, UserModel.last_name, UserModel.father_name,
               UserModel.email, UserModel.role, UserModel.about, UserModel.photo).where(UserModel.id_u == teamlead_id))
    for i in result.all():
        res_dict.append({"id": i[0],
                         "first_name": i[1],
                         "last_name": i[2],
                         "father_name": i[3],
                         "email": i[4],
                         "role": i[5],
                         "about": i[6],
                         "photo": i[7],
                         "type": "teamlead"})
    return JSONResponse(status_code=200, content={"detail": res_dict})


@router.delete("/team")
async def delete_team(id_u: int, payload: dict = Depends(token.check),
                      session: AsyncSession = Depends(db_session.get_async_session)):
    await user_exists(session, id_u)
    result = await session.execute(select(TeamLeadModel.team).where(TeamLeadModel.user == id_u))
    team = result.fetchone()
    if team is None:
        return JSONResponse(status_code=200, content={"detail": "Данный пользователь не является тимлидом"})
    await session.execute(delete(TeamModel).where(TeamModel.id_t == team[0]))
    await session.commit()
    return JSONResponse(status_code=200, content={"detail": "Успешно."})


@router.get("/send_notification_add")
async def send(id_u: int, id_t: int,
               session: AsyncSession = Depends(db_session.get_async_session)):
    result = await session.execute(
        select(TeamModel.name).where(TeamModel.id_t == id_t))
    team_data = result.fetchone()
    result = await session.execute(
        select(UserModel.email, UserModel.first_name, UserModel.last_name).where(UserModel.id_u == id_u))
    user_data = result.fetchone()
    send_notification_add.delay(user_data[0], user_data[1], user_data[2], team_data[0])
    return JSONResponse(status_code=200, content={"detail": "Успешно."})


@router.get("/send_notification_delete")
async def send(id_u: int,
               session: AsyncSession = Depends(db_session.get_async_session)):
    result = await session.execute(
        select(UserModel.team).where(UserModel.id_u == id_u))
    user_id = result.fetchone()[0]
    result = await session.execute(
        select(TeamModel.name).where(TeamModel.id_t == user_id))
    team_data = result.fetchone()
    result = await session.execute(
        select(UserModel.email, UserModel.first_name, UserModel.last_name).where(UserModel.id_u == id_u))
    user_data = result.fetchone()
    print(team_data, user_data)
    send_notification_delete.delay(user_data[0], user_data[1], user_data[2], team_data[0])
    return JSONResponse(status_code=200, content={"detail": "Успешно."})


@router.get('/all_teams', summary="Get all teams")
async def all_teams(session: AsyncSession = Depends(db_session.get_async_session)):
    res_dict = []
    result = await session.execute(
        select(TeamModel.id_t, TeamModel.name, TeamModel.about, TeamModel.banner).where(1 == 1))
    for i in result.all():
        res_dict.append({"id_t": i[0],
                         "name": i[1],
                         "about": i[2],
                         "banner": i[3]})
    return JSONResponse(status_code=200, content=res_dict)


@router.post('/job', summary="Add job")
async def add_job(schema: AddJobSchema, payload: dict = Depends(token.check),
                  session: AsyncSession = Depends(db_session.get_async_session)):
    stmt = insert(JobModel).values(
        github=schema['github'])
    await session.execute(statement=stmt)
    await session.commit()
    return JSONResponse(status_code=200, content={"detail": "Работа успешно добавлена."})

@router.get('/all_job', summary="Get all jobs")
async def all_case(session: AsyncSession = Depends(db_session.get_async_session)):
    res_dict = []
    result = await session.execute(
        select(JobModel.id_j, JobModel.github, JobModel.file, JobModel.case).where(1 == 1))
    for i in result.all():
        res_dict.append({"id_j": i[0],
                         "github": i[1],
                         "file": i[2],
                         "case": i[3]})
    return JSONResponse(status_code=200, content=res_dict)