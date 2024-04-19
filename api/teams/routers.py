from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse

from api.auth.models import UserModel
from api.teams.models import TeamModel, TeamLeadModel
from api.teams.schemas import TeamCreateSchema
from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from database import db_session

router = APIRouter(
    prefix="/teams",
    tags=["Teams"]
)


@router.post("/team")
async def create_team(schema: TeamCreateSchema, session: AsyncSession = Depends(db_session.get_async_session)):
    schema = schema.model_dump()
    stmt = insert(TeamModel).values(name=schema['name'], about=schema['about'])
    await session.execute(stmt)
    query = select(TeamModel.id_t).where(TeamModel.name == schema["name"])
    result = await session.execute(query)
    stmt = insert(TeamLeadModel).values(user=schema["id_u"], team=result.fetchone()[0])
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(status_code=200, content={"detail": "Команда была добавлена."})


@router.get("/team")
async def get_team_by_user(id_u: int, session: AsyncSession = Depends(db_session.get_async_session)):
    result = await session.execute(select(UserModel.email).where(UserModel.id_u == id_u))
    user_email = result.fetchone()
    if user_email is None:
        raise HTTPException(
            status_code=400,
            detail="Пользователя с таким id не существует."
        )
    result = await session.execute(select(UserModel.team).where(UserModel.id_u == id_u))
    team = result.fetchone()
    if team[0] is None:
        result = await session.execute(select(TeamLeadModel.team).where(TeamLeadModel.user == id_u))
        team = result.fetchone()
        if team is None:
            return JSONResponse(status_code=200, content={"detail": ""})

    result = await session.execute(
        select(TeamLeadModel.id_tl, TeamModel.name, TeamModel.banner).where(TeamModel.id_t == team[0]))
    team_user = result.fetchone()
    return JSONResponse(status_code=200, content={"detail": {"id": team_user[0],
                                                             "name": team_user[1],
                                                             "about": team_user[2]}})
