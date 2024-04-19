from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse

from api.auth.models import UserModel
from api.teams.models import TeamModel, TeamLeadModel
from api.teams.schemas import TeamCreateSchema, AddUserSchema, TeamPatchSchema
from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from api.auth.utils import token
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
    query = select(TeamModel.id_t).where(TeamModel.name == schema["name"])
    result = await session.execute(query)
    stmt = insert(TeamLeadModel).values(user=schema["id_u"], team=result.fetchone()[0])
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(status_code=200, content={"detail": "Команда была добавлена."})


@router.get("/team")
async def get_team_by_user(id_u: int, payload: dict = Depends(token.check),
                           session: AsyncSession = Depends(db_session.get_async_session)):
    await user_exists(session, id_u)
    result = await session.execute(select(UserModel.team).where(UserModel.id_u == id_u))
    team = result.fetchone()
    if team[0] is None:
        result = await session.execute(select(TeamLeadModel.team).where(TeamLeadModel.user == id_u))
        team = result.fetchone()[0]
        if team is None:
            return JSONResponse(status_code=200, content={"detail": ""})

    result = await session.execute(
        select(TeamModel.id_t, TeamModel.name, TeamModel.about,TeamModel.banner).where(TeamModel.id_t == team))
    team_user = result.fetchone()
    return JSONResponse(status_code=200, content={"id_t": team_user[0],
                                                  "name": team_user[1],
                                                  "about": team_user[2],
                                                  "banner": team_user[1],})


@router.patch("/team")
async def patch_team(schema: TeamPatchSchema, payload: dict = Depends(token.check),
                     session: AsyncSession = Depends(db_session.get_async_session)):
    schema = schema.model_dump()
    result = await session.execute(select(
        TeamModel.name, TeamModel.about).where(
        TeamModel.id_t == schema["id_t"]))
    result = result.fetchone()
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


@router.post("/user")
async def add_user_to_team(schema: AddUserSchema, payload: dict = Depends(token.check),
                           session: AsyncSession = Depends(db_session.get_async_session)):
    schema = schema.model_dump()
    stmt = update(UserModel).where(UserModel.id_u == schema['id_u']).values(team=schema['id_t'])
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(status_code=200, content={"detail": "Пользователь был успешно добавлен."})


@router.delete("/user")
async def add_user_to_team(id_u: int, payload: dict = Depends(token.check),
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
        res_dict.append({"member": {"id": i[0],
                                    "first_name": i[1],
                                    "last_name": i[2],
                                    "father_name": i[3],
                                    "email": i[4],
                                    "role": i[5],
                                    "about": i[6],
                                    "photo": i[7]}})
    result = await session.execute(select(TeamLeadModel.user).where(TeamLeadModel.team == id_t))
    teamleam_id = result.fetchone()[0]
    result = await session.execute(
        select(UserModel.id_u, UserModel.first_name, UserModel.last_name, UserModel.father_name,
               UserModel.email, UserModel.role, UserModel.about, UserModel.photo).where(UserModel.id_u == teamleam_id))
    for i in result.all():
        res_dict.append({"teamlead": {"id": i[0],
                                      "first_name": i[1],
                                      "last_name": i[2],
                                      "father_name": i[3],
                                      "email": i[4],
                                      "role": i[5],
                                      "about": i[6],
                                      "photo": i[7]}})
    return JSONResponse(status_code=200, content=res_dict)


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
