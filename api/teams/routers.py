from fastapi import Depends
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.sql import text
from api.auth.models import UserModel
from api.teams.models import TeamModel
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
    stmt = insert(TeamModel).values(name=schema['name'])
    await session.execute(stmt)
    stmt = insert(Te)
    await session.execute(text(
        f"""INSERT INTO teamlead(user, team) values("{schema['id_u']}", (SELECT id_t FROM team WHERE name={schema['name']}));"""))

    await session.commit()
    return JSONResponse(status_code=200, content={"detail": "Команда была добавлена."})


@router.get("/team")
async def get_team_by_user(id_u: int, session: AsyncSession = Depends(db_session.get_async_session)):
    result = await session.execute(
        text(f"""SELECT * FROM team WHERE id_t = (SELECT team FROM user WHERE id_u = {id_u})"""))
    result = result.fetchone()
    return JSONResponse(status_code=200, content={"detail": result})
