import datetime
from typing import Union, Any

from fastapi import HTTPException
from fastapi.requests import Request
from jose import jwt
from passlib.context import CryptContext

from config import SECRET_JWT_ACCESS, SECRET_JWT_REFRESH


class Password:
    def __init__(self):
        self.password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        return self.password_context.hash(password)

    def verify(self, password: str, hashed_pass: str) -> bool:
        return self.password_context.verify(password, hashed_pass)

    @staticmethod
    def check(password: str) -> bool:
        if len(password) < 8:
            raise HTTPException(status_code=400, detail="Пароль должен содержать минимум 8 символов.")
        if password.isdigit():
            raise HTTPException(status_code=400,
                                detail="Пароль должен содержать минимум 2 буквы разных регистров.")
        if password.islower():
            raise HTTPException(status_code=400,
                                detail="Пароль должен содержать минимум 2 буквы разных регистров.")
        if password.isupper():
            raise HTTPException(status_code=400,
                                detail="Пароль должен содержать минимум 2 буквы разных регистров.")
        if password.isalnum():
            raise HTTPException(status_code=400,
                                detail="Пароль должен содержать минимум 1 специальный символ.")
        if password.isalpha():
            raise HTTPException(status_code=400,
                                detail="Пароль должен содержать минимум минимум 1 цифру.")
        return True


class TokenData:
    def __init__(self,
                 access_time: int = 60, # 15 minutes
                 refresh_time: int = 60 * 24 * 7 * 2, # 14 days
                 algorithm: str = "HS256"):

        self.ACCESS_TOKEN_EXPIRE_MINUTES = access_time
        self.REFRESH_TOKEN_EXPIRE_MINUTES = refresh_time
        self.ALGORITHM = algorithm
        self._JWT_ACCESS_SECRET_KEY = SECRET_JWT_ACCESS
        self._JWT_REFRESH_SECRET_KEY = SECRET_JWT_REFRESH


class Token(TokenData):
    def create(self, subject: Union[str, Any], type_: str) -> str:
        if type_ == "access":
            expire = self.ACCESS_TOKEN_EXPIRE_MINUTES
            key = self._JWT_ACCESS_SECRET_KEY
        elif type_ == "refresh":
            expire = self.REFRESH_TOKEN_EXPIRE_MINUTES
            key = self._JWT_REFRESH_SECRET_KEY
        else:
            raise ValueError("Неверно указан тип токена")
        expires_delta = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            minutes=expire)
        to_encode = {"exp": expires_delta, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, key, self.ALGORITHM)
        return encoded_jwt

    async def check(self, request: Request, type_: str = "access") -> dict:
        try:

            try:
                authorization = request.headers.get("Authorization").split(" ")
            except AttributeError:
                raise HTTPException(
                    status_code=400,
                    detail="Отсутствует заголовок с токеном."
                )

            if authorization[0] != "Selezenka":
                raise HTTPException(status_code=400, detail="Не угадал.")
            if type_ == "access":
                payload = jwt.decode(authorization[1], self._JWT_ACCESS_SECRET_KEY, algorithms=[self.ALGORITHM])
            elif type_ == "refresh":
                payload = jwt.decode(authorization[1], self._JWT_REFRESH_SECRET_KEY, algorithms=[self.ALGORITHM])
            else:
                raise ValueError("Неверно указан тип токена")
            if datetime.datetime.fromtimestamp(payload["exp"]) < datetime.datetime.now():
                raise HTTPException(
                    status_code=401,
                    detail="Срок действия токена истёк."
                )
        except jwt.JWTError:
            raise HTTPException(
                status_code=403,
                detail="Не удалось подтвердить учетные данные."
            )
        return payload


password = Password()
token = Token()
