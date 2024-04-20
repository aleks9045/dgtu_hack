import os
from email.message import EmailMessage

import aiofiles
from fastapi import Depends, HTTPException, UploadFile, File
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from api.teams.tasks import send_notification_add, send_notification_delete

from api.auth.models import UserModel
from api.teams.models import TeamModel, TeamLeadModel
from api.invites.models import InviteModel
from api.teams.schemas import TeamCreateSchema, AddUserSchema, TeamPatchSchema
from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from api.auth.utils import token
from api.teams.utils import user_exists
from database import db_session

router = APIRouter(
    prefix="/invites",
    tags=["Invites"]
)


@router.post("/invite")
async def add_invite(schema: AddUserSchema, payload: dict = Depends(token.check),
                     session: AsyncSession = Depends(db_session.get_async_session)):
    schema = schema.model_dump()
    print(schema)
    stmt = insert(InviteModel).values(user=schema['id_u'], team=schema["id_t"])
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(status_code=200, content={"detail": "Пользователь был успешно приглашен."})


@router.get("/invite_by_user")
async def get_all_invites_by_user(id_u: int, payload: dict = Depends(token.check),
                                  session: AsyncSession = Depends(db_session.get_async_session)):
    res_dict = []
    result = await session.execute(
        select(InviteModel.id_i, InviteModel.user, InviteModel.team).where(InviteModel.user == id_u))
    invite = result.fetchall()
    for i in invite:
        result = await session.execute(
            select(TeamModel.id_t, TeamModel.name, TeamModel.about, TeamModel.banner).where(TeamModel.id_t == i[2]))
        team_user = result.fetchone()
        res_dict.append({"id_i": i[0],
                         "id_u": i[1],
                         "team": {"id_t": team_user[0],
                                  "name": team_user[1],
                                  "about": team_user[2],
                                  "banner": team_user[3]}})
    return JSONResponse(status_code=200, content=res_dict)


@router.get("/invite_by_team")
async def get_all_invites_by_team(id_t: int, payload: dict = Depends(token.check),
                                  session: AsyncSession = Depends(db_session.get_async_session)):
    res_dict = []
    result = await session.execute(
        select(InviteModel.id_i, InviteModel.user, InviteModel.team).where(InviteModel.team == id_t))
    invite = result.fetchall()
    for i in invite:
        res_dict.append({"id_i": i[0],
                         "id_u": i[1],
                         "id_t": i[2]})
    return JSONResponse(status_code=200, content=res_dict)


@router.delete("/invite_accept")
async def invite_accept(schema: AddUserSchema, payload: dict = Depends(token.check),
                        session: AsyncSession = Depends(db_session.get_async_session)):
    stmt = update(UserModel).where(UserModel.id_u == schema["id_u"]).values(team=schema["id_t"])
    await session.execute(stmt)
    stmt = delete(InviteModel).where(InviteModel.user == schema["id_u"])
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(status_code=200, content={"detail": "Пользователь был успешно добавлен."})


@router.delete("/invite_refuse")
async def invite_refuse(schema: AddUserSchema,
                        session: AsyncSession = Depends(db_session.get_async_session)):
    stmt = delete(InviteModel).where(InviteModel.user == schema["id_u"], InviteModel.team == schema["id_t"])
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(status_code=200, content={"detail": "Пользователь был успешно удалён."})
