from fastapi import HTTPException
from sqlalchemy import select

from api.auth.models import UserModel


async def user_exists(session, id_u: int):
    result = await session.execute(select(UserModel.email).where(UserModel.id_u == id_u))
    user_email = result.fetchone()
    if user_email is None:
        raise HTTPException(
            status_code=400,
            detail="Пользователя с таким id не существует."
        )
