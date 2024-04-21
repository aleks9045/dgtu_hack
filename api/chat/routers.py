import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse, JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from api.chat.utils import ws_manager
from api.experts.models import CompanyModel, CaseModel
from api.teams.models import TeamModel, JobModel
from database import db_session

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.get("/")
async def get():
    return FileResponse("templates/chat/index.html")


@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        new_one = json.loads(await websocket.receive_text())
        await ws_manager.connect(new_one, websocket)
        while True:
            data = json.loads(await websocket.receive_text())
            await ws_manager.send_message(data)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


@router.get("/chat_id")
async def get_chat_id(clue: int, session: AsyncSession = Depends(db_session.get_async_session)):
    res_chat_id = ""
    result = await session.execute(select(TeamModel.id_t).where(TeamModel.id_t == clue))
    id_t = result.fetchone()[0]
    if id_t is None:
        result = await session.execute(select(CompanyModel.id_co).where(CompanyModel.id_co == clue))
        id_co = result.fetchone()[0]
        if id_co is None:
            raise HTTPException(status_code=404, detail="Не существует такой команды или компании.")
        else:
            result = await session.execute(
                select(CaseModel.id_ca).where(CaseModel.company == id_co))
            id_ca = result.fetchone()[0]
            res_chat_id += id_ca
            result = await session.execute(
                select(JobModel.id_j, JobModel.team).where(JobModel.case == id_ca))
            result = result.fetchone()
            id_j = result[0]
            team = result[1]
            res_chat_id += id_j
            result = await session.execute(
                select(TeamModel.id_t).where(TeamModel.id_t == team))
            id_t = result.fetchone()[0]
            res_chat_id += id_t
            res_chat_id = ''.join(sorted(res_chat_id))
            return JSONResponse(status_code=200, content={"chat_id": str(res_chat_id)})
    else:
        result = await session.execute(
            select(JobModel.id_j).where(JobModel.team == id_t))
        id_j = result.fetchone()[0]
        result = await session.execute(
            select(CaseModel.id_ca).where(CaseModel.company == id_co))
        id_ca = result.fetchone()[0]
        res_chat_id += id_ca
        result = await session.execute(
            select(JobModel.id_j, JobModel.team).where(JobModel.case == id_ca))
        result = result.fetchone()
        id_j = result[0]
        team = result[1]
        res_chat_id += id_j

        res_chat_id += id_t
        res_chat_id = ''.join(sorted(res_chat_id))
